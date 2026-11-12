# Claude Code handoff 5 — transcription of phone photos IMG_9022, 9023, 9024, 9025

Follows `claude_code_handoff.md` to `_4.md`. Read together. This batch is a third file: `tmp_validation/a1_bureau_fill/summary_baseline.md` (the *baseline rerun* of the A1 bureau fill, same folder as handoff 2's `summary.md`).

## Context
- VS Code, dev container `cdp-devcontainer:latest @ 10.119.132.99`, workspace `retail.collections.risk_profiling`.
- Open tabs: `pipeline_registry.py`, `primary.py`, `24_a1_product_primaries_bureau_swap.md`, `summary_baseline.md` (active, saved).
- Breadcrumb: `tmp_validation > a1_bureau_fill > summary_baseline.md > # A1 bureau fill, baseline rerun: summary (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus)`
- Git blame on line 1: "You, 1 minute ago • A1 bureau salary [cut off]" (the file is newly written).
- Photos overlap (L1-58, L53-108, L106-162, L147-203), so I merged them into one continuous file of 203 lines. Word wrap is on; I omitted line numbers.

---

## `tmp_validation/a1_bureau_fill/summary_baseline.md`

````markdown
# A1 bureau fill, baseline rerun: summary (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus)

Source: `results_baseline_<model_id>.md` of this folder (PROD run 2026-11-12, `a1_bureau_baseline_snippet.py`); no part failed in any model_id. Alert levels come from the RAW salary alerts (`prm_bureau_alert_enriched`), dated 2024-01 or later, `salaryaccountclosed` = a stop whatever its amount. Alert age = months since the latest alert at or before the month; the age bands stop at the persona end month 2026-08, "did an alert come" looks up to 2026-11. Column labels: cc60 = cc_60_180, rl160 = rl_60_180, cc180 = cc_180_plus, rl1180 = rl_180_plus. A cell under 10 is `<10`; * = the 95% CI (clustered on CIF) excludes 0.

## 1. Verdict per age band: does "no alert = no change" hold?

| Age | Verdict | Deciding numbers |
|---|---|---|
| 1 | Yes | internal within CIF +0.6pp cc60 (n.s.); moved 20% = 19% where alert changed; stops not testable |
| 2-3 | Yes | stops 0.5-1.1% of fill months, 55-68% are bank moves, net 0.2-0.5%; credit -10 to -14pp* |
| 4-6 | Unclear | net stops 1.3-3.1%; internal flat within CIF (cc); credit -13 to -14pp* (cc60, cc180) |
| 7-12 | No | net stops 6.6-8.2% (~1 in 13); internal >25% higher 37-47% (33-40% fresh); credit -15 to -21pp* |
| 13-24 | No | net stops 21-31%; internal >25% higher 45-63%, median internal/alert 1.1-1.5 |
| 25+ | No | net stops 44-52% of fill months |

- **Fill up to ~3 months is supported; 4-6 months only if the stop mapping is fixed first (section 8); beyond 6 months the data say no.** Age 1 cannot show stops by construction (a stop needs 2 months of no internal salary after a level dated on or before the last salary month), so age 1 rests on the disagreement tests alone.
- Net stops are an upper bound of true salary stops: "nothing" also holds salary that moved to a bank we cannot see.

## 2. Test 1: disagreement by alert age, against age 0

**The baseline is high.** A fresh alert (age 0) already disagrees with every comparator:

| Within 10% of the alert level at age 0 | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| internal salary | 19.3% | 22.4% | 18.1% | 21.2% |
| `salary_credit` | 56.9% | 50.8% | 64.0% | 48.8% |
| pull (DE label, lag 0) | 29.7% | 28.5% | 32.7% | 39.3% |
| CIF-months, internal | 1,943 | 674 | 1,221 | 391 |
| CIF-months, credit | 2,362 | 179 | 1,695 | 41 |
| CIF-months, pull | 1,245 | 172 | 153 | 56 |

**Internal salary, within CIF** (CIFs with a comparison at age 0 and in the band; change in the share within 10%):

| Age | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| 1 | +0.6pp (693) | -4.5pp (282) | -1.4pp (396) | -8.5pp* (142) |
| 2-3 | +2.0pp (546) | -2.7pp (220) | +0.6pp (316) | -8.6pp* (109) |
| 4-6 | -0.3pp (240) | -7.5pp* (95) | -3.8pp (133) | -11.0pp* (44) |
| 7-12 | -1.8pp (117) | -2.0pp (49) | +1.1pp (54) | -11.2pp (23) |
| 13-24 | -9.9pp (24) | +1.9pp (13) | <10 | <10 |

Up to 6 months, internal agreement is no lower than at age 0 in 8 of 12 model x band cells; the four that are lower are RL (r160 4-6, r1180 1, 2-3, 4-6). Beyond 6 months the within-CIF samples are too small (<=117 CIFs) to settle it, but the pooled rows show where the fill drifts: internal is above the alert in more and more cases.

| Internal, pooled: >25% higher than the alert | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| age 0 | 32.6% | 36.4% | 32.9% | 39.6% |
| 4-6 | 33.4% | 29.0% | 31.0% | 27.8% |
| 7-12 | 40.8% | 45.2% | 36.9% | 46.5% |
| 13-24 | 48.4% | 60.5% | 45.1% | 62.5% |
| median internal / alert, 13-24 | 1.22 | 1.43 | 1.11 | 1.50 |

**`salary_credit`, within CIF** (share within 10%, change against age 0; the credit and the alert are the same bureau record at age 0, so the first step is partly mechanical):

| Age | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| 1 | -3.8pp* (529) | -6.1pp (51) | -10.9pp* (396) | -5.1pp (13) |
| 2-3 | -10.5pp* (444) | -5.8pp (47) | -13.7pp* (330) | -5.6pp (12) |
| 4-6 | -13.4pp* (315) | -2.3pp (31) | -14.4pp* (225) | +15.9pp (11) |
| 7-12 | -20.7pp* (157) | -11.4pp (17) | -15.2pp* (91) | <10 |

Where it moves, it moves to "credit lower than the alert" (cc60 more than 25% lower: 18.5% at age 0, 34-43% at 1-12 months).

**Pull (lag 0), within CIF:** no deterioration. Share within 10% changes +4.9pp* (age 1) and +8.5pp* (2-3) in cc60, +9.2pp / +16.6pp* in cc180, +2.4pp / +6.2pp in r160 (n.s.); r1180 and ages 7+ are <10 or CIs span 0.

## 3. Test 2: does the comparator move while the alert is silent?

Share of silent CIF-months where the comparator moved >25% since the alert month, and, in brackets, the same movement over the same horizon where the alert did change (new level >10% away or a stop). Internal = median of 3 months.

| Internal salary, silent (changed) | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| 1 | 19.6% (19.1%) | 21.6% (18.9%) | 20.3% (21.0%) | 18.6% (21.9%) |
| 2-3 | 27.3% (32.4%) | 33.5% (29.9%) | 30.2% (33.1%) | 29.1% (32.1%) |
| 4-6 | 34.7% (37.0%) | 35.8% (39.3%) | 38.6% (39.1%) | 44.0% (43.7%) |
| 7-12 | 40.6% (40.7%) | 42.5% (37.7%) | 41.3% (44.6%) | - |
| 13-24 | 50.0% (45.6%) | 37.0% (54.3%) | - | - |

| `salary_credit`, silent (changed) | cc60 | r160 | cc180 |
|---|---|---|---|
| 1 | 27.1% (39.5%) | 27.8% (36.6%) | 26.8% (45.4%) |
| 2-3 | 33.1% (44.0%) | 34.6% (43.8%) | 32.9% (47.7%) |
| 4-6 | 34.1% (43.7%) | 38.0% (44.4%) | 37.2% (46.8%) |
| 7-12 | 33.4% (44.7%) | 55.4% (43.6%) | 30.5% (53.8%) |

- **Internal and pull move as much when the alert is silent as when it changed** (cc60 pull: 14% vs 14%, 27% vs 29%, 44% vs 43% at 1, 2-3, 4-6 months). Their movement does not separate silence from change, so it cannot show that silence means "no change"; it is mostly noise (bonuses, allowances), and equally present at 1 month.
- **`salary_credit` moves less when silent (27-38% vs 37-54%; r160 at 7-12 months is the exception, 55% vs 44%)**, but still in a quarter to a third of the cases from month 1.
- **Alert follows a moved internal salary:** within 3 months in 75% (age 1) -> 61% (2-3) -> 42% (4-6) -> 14% (7-12) in cc60, "never" (to 2026-11) 7% -> 13% -> 25% -> 51% -> 62% (13-24). RL and 180+ look alike (never at 4-6: 31% r160, 15% cc180, 27% r1180). Recent months are censored, so "never" is overstated at the old end.

## 4. Test 3: stops on the raw series, net of bank moves

Fill months with internal history: 32,875 / 10,377 / 34,536 / 11,259 (cc60 / r160 / cc180 / r1180). Stop = internal salary steady for 3 months, then nothing for 2+ months, level dated on or before the last salary month, no raw 0 / closed alert yet. Table: stop share of fill months, and in brackets the share left after removing bank moves (`salaryaccountadded` within +-2 months) and cases where `salary_credit` or the pull stays positive ("nothing").

| Age | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| 2-3 | 1.0% (0.4%) | 1.1% (0.5%) | 0.5% (0.2%) | 0.7% (0.5%) |
| 4-6 | 3.1% (2.3%) | 3.8% (3.1%) | 1.7% (1.3%) | 2.4% (2.3%) |
| 7-12 | 7.3% (6.8%) | 8.5% (8.2%) | 7.1% (6.6%) | 7.9% (7.8%) |
| 13-24 | 23.8% (23.4%) | 21.0% (20.6%) | 29.3% (28.9%) | 31.6% (31.2%) |
| 25+ | 46.2% (46.0%) | 50.0% (49.2%) | 44.1% (44.1%) | 52.9% (52.0%) |
| all | 4.7% (4.3%) | 6.6% (6.2%) | 4.3% (4.0%) | 6.8% (6.6%) |

- **Bank moves explain most early stops, none of the late ones:** at 2-3 months 56 of 95 stops (cc60) and 38 of 56 (cc180) have a `salaryaccountadded` alert nearby; at 7-12 months 10 of 308 and 18 of 303. `salary_credit` / pull still positive after the stop is rare (<10 to 32 cases), because those sources are thin.
- Net stops grow with age (cc60): 1 in 250 fill months at 2-3 months, 1 in 43 at 4-6, 1 in 15 at 7-12, 1 in 4 at 13-24. These rates are on the raw series, i.e. already with `salaryaccountclosed` counted as a stop (section 8, point 1).

## 5. Test 4: how late stops arrive

| | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| CIFs with an internal stop and an active level | 462 | 186 | 322 | 134 |
| ... that got a 0 / closed alert by 2026-11 | 60.8% | 47.8% | 60.2% | 49.3% |
| lag, months (quartiles; 0 = alert in the first month) | 1 / 3 / 7 | 0 / 2 / 5 | 1 / 3 / 8 | 1 / 3 / 8 |
| lag 7+ months, of those with an alert | 28.1% | 12.4%+ | 32.0% | 33.4% |
| lag 0 | 18.5% | 25.8% | 24.2% | 24.2% |

The lag cannot be negative here (the level must be active at the last internal month). Four in ten to half of the CIFs with an internal stop get no stop alert by 2026-11 (40-52%); of those that do, an eighth to a third arrive 7+ months late.

**The 2026-07 bulk month looks like a catch-up of late stops.** Share of 0 / closed alerts whose CIF had been silent 7+ months, 2026-07 vs other months: cc60 13.8% vs 7.6%, r160 14.8% vs 5.6%, cc180 13.3% vs 5.8%, r1180 13.0% vs 4.9%. In other months 18-21% of the 0 alerts have no earlier level since 2024-01 (a stop with no level before it), against 3-7% in July.

## 6. Pull booking month

| Within 10% of the alert level, alert age 0 | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| lag 0 (DE label) | 28.1% | 26.0% | 30.7% | 38.3% |
| lag -1 (pull month m vs alert month m-1) | 27.5% | 26.0% | 33.6% | 34.0% |
| CIF-months | 1,125 | 150 | 137 | 47 |
| pull vs internal, best label shift k | 0 | 0 | 0 | n/a |

The two lags are indistinguishable at age 0 (CIs overlap everywhere; 180+ has 47-137 CIF-months). The larger test, the pull against internal salary at label shifts -2..+2, is best at k = 0 in cc60 (43.8% within 10% vs 38.8% at +1), r160 (29.5% vs 28.6%) and cc180 (48.4% vs 43.7%). **No sign that the pull is booked one month late; keep the DE's label.** It changes nothing downstream. Pull agreement with the alert is low either way (26-39% within 10% fresh).

## 7. How many of the first run's missed stops were hidden 0 alerts

Last 24 months, fill from the unified `alert` rows (the first run's input), split by what the RAW series says:

| Share of the first run's missed stops | cc60 | r160 | cc180 | r1180 |
|---|---|---|---|---|
| raw 0 / closed alert hidden by a `salary_credit` / pull row | 7.6% | 6.5% | 3.6% | 1.8% |
| raw 0 / closed alert later than the unified alert, no other source | 34.0% | 43.2% | 30.7% | 34.5% |
| closed alert with an amount > 0, shown as a level | 3.6% | 0.8% | 2.7% | 0.0% |
| **not missed on the right data** | **45.2%** | **50.5%** | **37.0%** | **36.3%** |
| still a missed stop on the raw series | 54.8% | 49.5% | 63.0% | 63.7% |
| missed-stop CIF-months here / first run | 2,839 / 4,008 | 1,390 / 2,088 | 2,337 / 2,398 | 1,199 / 1,244 |

**Reproduction caveat.** The CIF-month counts here match the first run within 2.5-3.6% in 180+, but are 29-33% lower in 60_180. This run's universe is the CIFs of `crx_<p>_obs_base`; the first run read the DE's wider scope, which probably holds stopped customers that are no longer observed. Read the shares as shares of the obs-base stops; the 180+ shares are the closest to the first run's population.

The biggest class is not the precedence but 0 alerts that do not reach the unified table at all. The most likely cause is `salaryaccountclosed` alerts with no amount, which the DE drops (`int_bureau_alert_salary_monthly` keeps only rows with `salary_credit_amount`); the data show the alerts exist, not why they are missing. The `salaryaccountisadded/closed` type also has 2,173 amount-less rows in cc60 (8,318 with a 0). The precedence hides only 2-8%.

## 8. For the DE, so that a fill is safe

1. **Map `salaryaccountclosed` to a stop (0) whatever its amount** (also when `salary_credit_amount` is NULL or > 0). This removes 33-44% of today's apparent missed stops. Decide with the bureau what `salaryaccountisadded/closed` means.
2. **Carry the alert state independently of the winning amount:** an `alert_stop` flag and the alert date on the CIF-month row (or an alert-state table), so a `salary_credit` / pull row can no longer hide a 0 alert.
3. **Publish the latest alert level, its date and its state per CIF-month** (the fill belongs upstream, in one place).
4. Keep the pull label as it is (section 6).
5. Monitor stops that never arrive: 40-52% of the CIFs with an internal stop have no 0 / closed alert by 2026-11.

## Notes and cleanup

- Internal salary is our bank only; a stop there can be a move. The "nothing" class is therefore an upper bound.
- All tests are at CIF-month level with CIF-clustered CIs where shown; within-CIF cells under 10 CIFs are not shown.
- No catalog file was added for this run. After the results are pasted back, delete `bb_common.py`, `bb_data.py`, `bb_tests.py`, `a1_bureau_baseline_snippet.py` and `results_baseline_*.md` in this folder (the first run's files stay until their own cleanup).
````

---

## Notes
- The photos are angled and slightly blurred. Please check dense numbers against the file. The least certain cells are the `<10` / `-` cells, the r1180 columns in section 2 and 3 tables, and the figures in section 7.
- Section 8 point 1 says "removes 33-44% of today's apparent missed stops"; this matches the 34.0-43.2% row in section 7, so I read it as printed.
- In "Notes and cleanup" the last bullet's file list (`bb_common.py`, `bb_data.py`; `bb_tests.py`, `a1_bureau_baseline_snippet.py`, `results_baseline_*.md`) wraps across two lines in the photo. I joined it as I read it: the first two files are the ones to delete after pasting results, and `bb_tests.py` etc. are listed in the second half of the sentence.
- The photos can't be saved as images from chat; this is the text transcription only.
