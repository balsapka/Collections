# Claude Code handoff 2 — transcription of phone photos IMG_9006, 9007, 9008, 9009, 9010, 9012

Follows `claude_code_handoff.md` (IMG_9005: Claude Code explanation of alert / salary_credit / bureau_salary in `origin/bureau-pipeline-analysis`). Read together.

## Context
- Photo 1 (IMG_9006): AECB (credit bureau) characteristics documentation, shown in a PDF viewer (Acrobat toolbar: "Find text or tools", "Share", "Sign in"; page size 8.27 x 11.69 in). Taskbar shows Teams/Outlook/Excel/Acrobat/VS Code/Edge icons.
- Photos 2-6 (IMG_9007-9012): VS Code, window title `retail.collections.risk_profiling [Dev Container: cdp-devcontainer:latest @ 10.119.132.99]`.
  - Tabs: `pipeline_registry.py`, `summary.md` (U = untracked)
  - Breadcrumb: `tmp_validation > a1_bureau_fill > summary.md > # A1 bureau fill: summary (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus)`
  - Word wrap is on; photos overlap (L1-59, L38-113, L78-163, L129-214, L172-268). I merged them into one continuous file below. Sticky-scroll headers at the top of photos 3-6 are not repeated.
  - No numbering was lost in the merge: the file ends at line 268 (last visible, blank).
- `IMG_9011` was not sent (the sequence skips from 9010 to 9012). Photos 5 and 6 overlap, so nothing in the text appears to be missing, but check the boundary at the end of section 4 ("Split by what other sources said").

---

## Photo 1 — AECB characteristics table (PDF)

The top of the page is cut off. Table columns: description | code | category.

| Description | Code | Category |
|---|---|---|
| [cut off at top] - '0' if info returned in Code #225 has no link with the enquiring provider; - '1' if info returned in Code #225 has link with the enquiring provider | 229 | (blank) |
| Sum of all current Other Income amount | 227 | Income - All Other Incomes |
| Newest Other Income last update date | 228 | (same merged cell) |
| Other Income Data Provider Flag: the system returns - '0' if info returned in Code #227 has no links with the enquiring provider - '1' if info returned in Code #227 has at least one link with the enquiring provider | 230 | (same merged cell) |
| The system returns: - The Income Utilization Ratio if available - NA if the Income Utilization Ratio is not available | 231 | IUR |
| Salaries reported for the last month | 232 | Income - Salary |
| Salaries reported for the last 3 months | 233 | Income - Salary |
| Salaries reported for the last 6 months | 234 | Income - Salary |
| Salaries reported for the last 12 months | 235 | Income - Salary |

Footnotes under the table:
- `* Operation Types 102, 103, 104 are not included within the calculation of these Characteristics`
- `** Characteristics 182 to 191: represent the worst values in the entire history among all active and closed contracts.`
- `*** Characteristics 192 to 201: represent the worst values in the latest reported month among all active and closed contracts.`
- `Characteristics 222, 223 and 224 are not available`

Layout note: the "Income - All Other Incomes" label sits in a merged cell spanning the rows for 227, 228 and 230. The cell beside 229 looks empty.

---

## Photos 2-6 — `tmp_validation/a1_bureau_fill/summary.md` (lines 1-268)

````markdown
# A1 bureau fill: summary (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus)

Source: `results_<model_id>.md` of this folder (PROD run 2026-11-12, snippet `a1_bureau_fill_snippet.py`). No part failed in any model_id. Persona end month 2026-08, W = 3 (60_180) / 6 (180+). Variants: C1 (level counts in its month and the next, a 0 ends it), C12 (fill to next alert / pull row or a 0, max 12 months), CU (no cap), CU-W (as CU, but a level older than W at the observation month is Weak only). Fills start only from levels dated 2024-01 or later. A cell under 10 is `<10`. Fill age = months since the level row.

## Headlines

1. **Check 0 PASSES in all four** (0 of 93,548 / 16,497 / 318,663 / 55,371 rows differ in `a1_income_level` or `a1_state`), and the C1 series built here equals the engine's own carry (0 CIF-months differ). C1 on the unified table moves 0.7-3.9% of income levels against today, so the unified swap with the carry is close to today.
2. **Silence is credible at feed level, not at salary level.** Beyond 4 months since the last salary alert, 77-95% of CIFs still get other alert types, so the feed is alive for them. But while a level is filled, the other sources disagree by more than 25% in 37-67% of the cases where they are present, and the fill outlives a stopped internal salary in 5-8% of fill months with internal history (28-32% at fill age 13+).
3. **A filled level does not decay, it starts lower.** Bureau-only Stable cures 14.8% when fresh (age 0-1) and 10.1-11.9% at every age from 2-3 to 13+ (cc_60_180): flat, no cliff, but a step down at the fill boundary, and only 0-2pp above no evidence (9.2%). It is on a level with persisted Low (10.9%), not Moderate (15.9%).
4. **Weak levels get worse when filled.** Filled Weak cures 3.8-7.5% (cc_60_180), below no evidence (9.2%).
5. **Missed stops are the one clearly bad group.** Filled Stable that outlived a stopped internal salary cures 1.1% (age 7-12, n=87) and 6.6% (13+, n=136) against 12% for clean fills (cc_60_180); RL shows the same direction.
6. **Recommendation: do not adopt CU or C12 as Stable evidence.** Keep C1 for Stable, and if the "silence = no change" semantics is wanted, fill as Weak evidence only. Detail in the last section.

## 0. Check 0 and series check  - verdict: PASS in all four

| | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| rows rebuilt | 93,548 | 16,497 | 318,663 | 55,371 |
| income level / state differ | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| C1 series vs engine carry (CIF-months) | 294,336, 0 differ | 36,321, 0 | 1,104,161, 0 | 100,154, 0 |

The comparison in questions 3 and 4 is like for like. C1 here carries `salary_credit` for no month (it is never filled), whereas the bundle design would carry it too; that is 2.5-8.5% of unified-evidence rows.

## 1. Feed health  - verdict: healthy; one step in 2025-01, one bulk month in 2026-07; silence is monitored

- **Latest `edp_load_date` seen: 2026-11-11** (latest `extract_date` 2026-11-11), all four. Series cut at 2026-08.
- **No gap month** (< 50% of the 3-month mean) from 2024-01 to 2026-08 in any model_id.
- **Two level shifts** (same in all four): alert rows jump 2025-01 (cc_60_180 7,053 -> 10,667, +51%; positive share 75% -> 90%), and 2026-07 is a bulk month (cc_60_180 16,018 rows = 156% of the 3 months before, of which 5,346 are 0 rows against ~1,100 a month before; rl_60_180 155%, cc_180_plus 154%, rl_180_plus 155%). 2026-08 returns to 88-94%. The 0 jump from 2026-07 noted in `a1_bureau_unified` is therefore a one-month bulk load, not a new regime.

Months since the last salary alert at 2026-08, CIFs with a positive alert since 2024-01, last alert positive (an active fill):

| | CIFs | p10 | p25 | p50 | p75 | p90 |
|---|---|---|---|---|---|---|
| cc_60_180 | 26,846 | 0 | 0 | 2 | 7 | 16 |
| rl_60_180 | 7,585 | 0 | 0 | 2 | 8 | 18 |
| cc_180_plus | 43,657 | 0 | 0 | 2 | 9 | 21 |
| rl_180_plus | 5,757 | 0 | 0 | 2 | 8 | 19 |

The last-24-months subset is shorter (cc_60_180 p75 6, p90 14). Of the CIFs with a bureau row, **45-51% have a 0 as their last row** (stopped), so the "a 0 ends it" rule decides about half of the population.

**CIFs whose latest positive level predates 2024** (C1 only, cannot be filled): cc_60_180 1,139 (2.2%), rl_60_180 524 (3.4%), cc_180_plus 3,864 (4.0%), rl_180_plus 446 (3.8%).

**Monitoring proxy** (share of active-fill CIFs with any other alert type after their last salary alert):

| months since last salary alert | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| 0-3 | 34.8% | 34.1% | 31.4% | 31.9% |
| 4-6 | 85.1% | 80.4% | 78.9% | 76.8% |
| 7-12 | 92.6% | 89.7% | 87.7% | 89.0% |
| 13-24 | 94.5% | 92.7% | 92.5% | 91.3% |
| 25+ | 93.9% | 90.4% | 90.0% | 89.1% |
| all | 57.0% | 55.8% | 54.5% | 54.2% |

(The 0-3 band is low by construction: few months to receive anything.) A CIF that has been silent on salary for 4+ months almost always still receives other alerts, so the feed covers it; 6-12% in the long bands get nothing and cannot be told apart from a CIF the bureau stopped reporting.

## 2. Disagreement while a fill is active  - verdict: few cases, but high disagreement rate; stops are missed

Base: alert-level fills, age >= 1, last 24 months, no alert that month: 418,677 CIF-months (cc_60_180), 114,174 (rl_60_180), 703,966 (cc_180_plus), 88,233 (rl_180_plus). As you expected, the other sources are rarely there.

Source present (share of fill CIF-months) and, where present, share more than 25% off the filled level (up + down):

| | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| internal salary present | 2.8% | 5.7% | 0.8% | 3.1% |
| ... > 25% off | 66.5% | 63.9% | 66.6% | 65.9% |
| ... within 10% | 20.6% | 23.8% | 21.0% | 22.6% |
| `salary_credit` present | 0.9% | 0.7% | 0.2% | 0.3% |
| ... > 25% off | 49.5% | 47.6% | 57.4% | 52.6% |
| ... within 10% | 39.0% | 42.1% | 32.4% | 36.9% |
| `bureau_salary` present | 0.7% | 0.6% | 0.1% | 0.1% |
| ... > 25% off | 43.5% | 47.2% | 37.4% | 41.6% |
| ... within 10% | 39.3% | 35.2% | 44.2% | 39.4% |

- Internal presence rises with fill age (cc_60_180 1.8% at age 1 -> 5.3% at 13+) and its agreement falls (within 10%: 23.4% -> 13.4%; more than 25% higher: 32.5% -> 43.3%): older fills sit increasingly below the internal salary. `salary_credit` and the pull are mostly lower than the filled level (credit > 25% lower 34.8%, pull 27.8% in cc_60_180), i.e. the fill overstates. Internal salary includes bonuses, so its disagreement is the weakest evidence; credit and pull are the cleaner comparators.
- RL application salary (reference): present 8.8% (rl_60_180) / 35.9% (rl_180_plus); within 10% only 25.6% / 16.7%.
- **Missed changes** (> 25% disagreements; did a new alert come?), cc_60_180:

| source (cc_60_180) | cases | caught in 1-3 months | later | never | open |
|---|---|---|---|---|---|
| internal | 7,831 | 28.4% | 25.9% | 40.5% | 5.2% |
| `salary_credit` | 1,809 | 50.5% | 36.3% | 12.8% | - |
| `bureau_salary` | 1,341 | 49.2% | 16.3% | 18.6% | 15.9% |

  When credit or pull disagrees, the alert follows within 1-3 months in about half the cases (alerts lag the other sources) and eventually in 65-91% of credit / pull cases. "Never" is 9-26% for credit and 18-49% for the pull (small counts at RL and 180+), and 38-50% for internal.
- **Missed stops** (fill active 2+ months after the internal salary stopped, no 0 alert), share of fill months with internal history:

| fill age | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| 2-3 | 0.8% | 0.9% | 0.6% | 0.7% |
| 4-6 | 3.0% | 3.8% | 2.2% | 3.0% |
| 7-12 | 9.4% | 10.6% | 8.8% | 9.6% |
| 13+ | 28.0% | 29.3% | 28.4% | 32.3% |
| all | 5.7% | 7.8% | 5.3% | 7.7% |

  Counts (CIF-months): 4,008 / 2,088 / 2,398 / 1,244. The latest internal month is 2026-08, so the last months are not thin. A stop is rare in the first 6 months and common after a year, which fits a salary that ends while the alert stays silent (a closed salary account would have fired a 43; it did not).

## 3. States  - verdict: CU and C12 add 8-10 points of Moderate; CU-W adds Low instead; C1 is today

Latest persona month. `a1_income_level` Stable and `a1_state` Moderate / Unknown, today -> variant:

| | today | C1 | C12 | CU | CU-W |
|---|---|---|---|---|---|
| cc_60_180 Stable | 15.5% | 14.5% | 23.6% | 25.4% | 18.8% |
| cc_60_180 Moderate | 14.8% | 13.9% | 21.9% | 23.4% | 17.7% |
| cc_60_180 Low | 25.6% | 27.3% | 31.3% | 31.2% | 37.0% |
| cc_60_180 Unknown | 58.0% | 57.2% | 45.2% | 43.6% | 43.6% |
| rl_60_180 Stable | 9.3% | 9.3% | 15.4% | 18.2% | 12.2% |
| rl_60_180 Moderate | 8.7% | 8.8% | 13.6% | 16.0% | 11.1% |
| rl_60_180 Unknown | 41.0% | 40.7% | 36.4% | 35.1% | 35.1% |
| cc_180_plus Stable | 6.7% | 6.6% | 9.6% | 11.4% | 8.8% |
| cc_180_plus Moderate | 6.2% | 6.0% | 8.8% | 10.5% | 8.1% |
| cc_180_plus Unknown | 85.2% | 85.1% | 82.6% | 81.0% | 81.0% |
| rl_180_plus Stable | 3.6% | 3.6% | 5.4% | 6.4% | 5.1% |
| rl_180_plus Moderate | 3.5% | 3.5% | 5.0% | 5.9% | 4.7% |
| rl_180_plus Unknown | 85.4% | 85.4% | 84.2% | 83.4% | 83.4% |

- Income-level moves, cc_60_180 (CU): none -> Stable 10.2%, none -> Weak 7.6%, Weak -> Stable 2.4%, Stable -> Weak 2.7% (C12, CU and CU-W alike, C1 1.9%: it is not an effect of the fill length). CU-W turns the none -> Stable rows into Weak (none -> Stable 3.6%, none -> Weak 14.1%).
- State moves, cc_60_180 (CU): Unknown -> Moderate 7.9%, Low -> Moderate 3.2%, Unknown -> Low 6.4%, Moderate -> Low 2.4%; unchanged 79.8% (C1 96.6%, CU-W 80.6%). High barely moves (1.6% -> 1.8%).
- 180+ moves are smaller in share (cc_180_plus CU: Unknown -> Moderate 3.4%, unchanged 93.9%) but large in rows: 10,932 accounts go Unknown -> Moderate.

### 3b. Filled levels older than the charge-off month (180+; 60_180 has no charge-off age, all 0)

| latest month, no internal salary | cc_180_plus | rl_180_plus |
|---|---|---|
| rows with any bureau level in W | 45,068 | 4,385 |
| ... level dated before the charge-off month | 9,957 (22.1%) | 716 (16.3%) |
| fill-only rows (no own / carry month in W) | 14,424 | 1,397 |
| ... level dated before the charge-off month | 7,458 (51.7%) | 546 (39.1%) |
| ... by fill age 2-3 / 4-6 / 7-12 / 13+ | 22.5 / 30.8 / 44.3 / 83.2% | 18.1 / 29.4 / 38.4 / 57.7% |

Charge-off month = observation month minus (`chargeoff_age_months` - 1), month-matched. Half of the filled evidence at 180+ was reported before the account was charged off, and 83% (CC) of the 13+ month fills. There are no 180+ outcomes, so these rows cannot be scored; by construction an old level there says nothing about the customer's means after charge-off.

## 4. Quality (60_180, Jan-May 2026 cohort)  - verdict: aged levels are Low-like; fill age does not matter, fresh does

cc_60_180, bureau-only rows (no internal, no `salary_credit`), `cure_3` / `pay_any_3` [95% CI clustered on CIF]:

| fill age | level | rows | cure_3 | pay_any_3 |
|---|---|---|---|---|
| 0-1 (today) | Stable | 15,040 | 14.8% [14.0, 15.6] | 41.0% [39.8, 42.2] |
| 2-3 | Stable | 3,153 | 10.1% [8.9, 11.3] | 30.1% [28.1, 32.0] |
| 4-6 | Stable | 2,681 | 11.3% [9.7, 12.8] | 32.2% [29.8, 34.5] |
| 7-12 | Stable | 2,201 | 11.9% [10.1, 13.7] | 30.5% [27.6, 33.4] |
| 13+ | Stable | 1,086 | 11.4% [8.8, 14.0] | 28.4% [23.9, 32.9] |
| 0-1 (today) | Weak | 4,030 | 11.4% [10.2, 12.6] | 32.4% [30.5, 34.3] |
| 2-3 | Weak | 1,060 | 5.0% [3.6, 6.4] | 14.5% [12.2, 16.8] |
| 4-6 | Weak | 546 | 3.8% [2.0, 5.7] | 16.7% [13.0, 20.3] |
| 7-12 | Weak | 393 | 4.3% [2.2, 6.5] | 16.3% [11.0, 21.5] |
| 13+ | Weak | 106 | 7.5% [0.5, 14.5] | 30.2% [16.4, 43.9] |

References (cc_60_180): internal Stable 18.9% / 42.4%, internal Weak 15.5% / 35.6%, no evidence 9.2% / 20.9%, today's bureau-only Stable 15.3% / 41.9%, persisted High 31.3% / 58.5%, Moderate 15.9% / 41.3%, Low 10.9% / 29.1%, Unknown 7.8% / 19.9%. (`salary_credit`-only Stable: n=41, not read.)

**The key test** (gaps, standardised to the better group's DPD mix, cc_60_180, Stable):

| filled Stable minus | 2-3 | 4-6 | 7-12 | 13+ |
|---|---|---|---|---|
| none, cure_3 | +0.1pp [-1.1, 1.4] | +1.4pp [-0.1, 3.0] | +2.0pp [0.3, 3.8] | +1.7pp [-0.8, 4.2] |
| none, pay_any_3 | +7.9pp [5.9, 9.9] | +10.2pp [7.8, 12.6] | +8.5pp [5.7, 11.4] | +6.6pp [2.4, 10.8] |
| fresh (0-1), cure_3 | -3.9pp [-5.2, -2.6] | -2.6pp [-4.2, -0.9] | -1.9pp [-3.8, -0.1] | -2.2pp [-4.7, 0.3] |
| fresh (0-1), pay_any_3 | -9.8pp [-11.9, -7.8] | -7.5pp [-10.0, -5.0] | -9.2pp [-12.2, -6.2] | -11.0pp [-15.3, -6.7] |

- A 7-12 month old Stable level **does** cure above none (+2.0pp) and still pays above none (+8.5pp), but it is **not near a fresh one** (-1.9pp cure, -9.2pp pay). A 13+ month level is the same within the interval. There is no age at which the level stops helping; the loss is already there at 2-3 months. A cap on cure grounds would have nothing to cut at.
- **Weak, filled**: below none on cure at every age up to 12 months (2-3: -3.9pp [-5.4, -2.4]; 4-6: -5.4pp; 7-12: -4.8pp [-7.0, -2.7]). The 13+ Weak cell (n=106) is not separable.
- **rl_60_180** (CIs are wide, n=163-272 per cell): Stable cure 13.4% fresh, 14.1% (2-3), 11.6% (4-6), 15.0% (7-12), 8.3% (13+) against none 11.0%; no filled gap to none on cure is separable (13+: -3.6pp [-9.6, 2.3]). `pay_any_3` is high for every bureau group in RL: fresh 66.6%, filled Stable 52-60%, none 43.4%; filled Stable - none is +13.3 to +15.3pp at 2-3, 4-6, 7-12 (CIs exclude 0) and 7-15pp below fresh (most CIs touch 0).
- **Split by what other sources said** (cc_60_180, filled Stable, cure_3): clean 10.1 / 11.4 / 12.4 / 11.9% at ages 2-3 / 4-6 / 7-12 / 13+; **missed stop 0.0% (4-6, n=16), 1.1% (7-12, n=87), 6.6% (13+, n=136)**; disagreement 0.0% (n=19), 9.3% (n=54), 13.7% (n=102), i.e. not separable from clean. `pay_any_3` for missed stops 13.8-19.1% against clean 29.7-32.3%. rl_60_180: missed stop 7-12 cure 6.5% (n=31) against clean 17.1%; 13+ 2.8% (n=36) against 7.1%. Only the missed stop marks a bad fill; a > 25% disagreement alone does not.
- Back-of-envelope from the table (approximate, row-weighted): the cc_60_180 filled rows (ages 2+) cure about 9.8% and pay about 27.9% overall, between none (9.2% / 20.9%) and Low (10.9% / 29.1%).

## Recommendation for the fill

**Do not adopt CU (the user's argument) or C12 as they stand.** Not because the level decays, it does not, but because a filled level is worth Low, and CU/C12 pay it as Stable (Moderate points).

1. **C1 stays the rule for Stable.** Fresh (age 0-1) bureau-only Stable cures like Moderate (14.8% vs 15.9%); from age 2 it cures like Low (10.1-11.9% vs 10.9%). CU moves 7.9% of cc_60_180 rows Unknown -> Moderate and 3.2% Low -> Moderate on that evidence (23.4% Moderate instead of 14.8%), which dilutes Moderate toward Low. CU-W with W = 3 still lets age 2-3 count as Stable (10.1%, -3.9pp against fresh), so it is also too generous for Stable.
2. **If "silence = no change" is wanted, fill as Weak evidence only** (a level older than 1 month: Weak, never Stable). That keeps the +8-10pp `pay_any_3` over none and puts the rows in Low (they look like Low: ~9.8% cure, ~27.9% pay), taking them out of Unknown (7.8% / 19.9%). Gain is small: cc_60_180 rows leaving Unknown for Low are about 11% of rows, and the measured Low-ness of the group is not better than none by much on cure. This is the CU-W rule with W = 1; **it was not run** (the runs used W = 3 / 6). It is a one-parameter rerun if you want its state table.
3. **Cap and stops.** Cure gives no cap (flat to 13+), the missed stop does: 28-32% of fill months with internal history at 13+ months, 9-11% at 7-12, 2-4% at 4-6. If a fill is kept as Weak, end it at 12 months (the 13+ band is where missed stops and the pre-charge-off levels pile up) and **end it when the internal salary has stopped** (the A1 engine already flags `a1_salary_stopped`; the missed-stop rows cure 1-7%). Only 15-17% of fill months have internal history, so this protects a minority.
4. **180+**: no outcomes, so no evidence for any fill. 52% (CC) / 39% (RL) of fill-only evidence is dated before the charge-off month; do not fill at 180+ without a charge-off cut (level dated before the charge-off month does not count), whatever is decided at 60_180.
5. **RL**: the cohort supports less than CC (cure gaps not separable; pay_any gaps are). Same rule, lower confidence.

## For the DE

- 2026-07 is a bulk month in the alert feed (about 155% of the 3 months before, 0 rows ~5x normal), all four spines. Reload, backfill or a change of the 0 rule? 2026-08 is back to normal.
- 2025-01 steps the alert rows up by 21-51% and the positive share from ~75% to ~90% (cc_60_180). Source change?
- A 0 alert in a month where `salary_credit` is usable is shown as the credit row (precedence), so the table hides some stops; a separate "alert 0" flag or an unfiltered alert series would let us end a fill on every stop.
- 45-51% of CIFs end on a 0. Is a 0 always a closed salary account (type 43), or also an alert with no amount?
- Alert coverage before 2024-01 (levels dated earlier cannot be filled: 2.2-4.0% of CIFs); can the DE confirm the 2024-01 start?
- Carried from `a1_bureau_unified`, still open: `salary_credit` thinning, `bureau_salary` only 2025-09 .. 2026-08, NULL `monthly_salary`.

## Caveats

- Cohort = Jan-May 2026, bucket 4-7, DPD-band standardised gaps only; no other control. The fresh group includes rows where an alert just fired (a change event), so "fresh minus filled" mixes level age with the event itself.
- Fill age is also a selection: customers whose alerts rarely fire (stable salary, or an unmonitored CIF) sit in the old bands. The monitoring proxy says most are monitored.
- Fills of pull levels (0.1-0.6% of rows) end part-2 fills in parts 3-4 but are comparators in part 2; their flags count as clean in the split. Flags exist only for fill months since 2024-02.
- The missed-stop test needs internal history, so it covers 15-17% of fill months; elsewhere the fill is untested.
- 180+ has no outcomes: the recommendation there rests on charge-off age and the 60_180 behaviour.
````

---

## Notes
- Photos were angled and slightly blurred. Dense numbers are the main OCR risk. Please check the figures against `summary.md` itself. The ones I'm least sure of are the CI brackets in the section 4 tables, the percentages in the section 3 state table, and the unusual numbers in headline 1 and section 0 (93,548 / 16,497 / 318,663 / 55,371; 294,336 / 36,321 / 1,104,161 / 100,154).
- The "silence is credible" headline (2) and the "Monitoring proxy" table use the same 77-95% range; I read both as printed.
- In "For the DE", the bullet about `salary_credit` thinning is the last line visible before the "## Caveats" heading.
- The photos can't be saved as images from chat; this is the text transcription only.
