> **Note (2026-11-12):** codes 232–235 are documented (AECB table in `bureau_fill_whatif_results.md`, handoff 2 photo 1): salaries reported for the last 1 / 3 / 6 / 12 months, cumulative. DE question 1 is answered except the look-back's reference date (response date vs `EDP_LOAD_DATE`).

# Claude Code handoff 3 — transcription of phone photos IMG_9017, 9018, 9019, 9020

Follows `claude_code_handoff.md` and `claude_code_handoff_2.md`. Read together. This batch is a different file from handoff 2: `tmp_validation/a1_bulk_pull/summary.md` (the A1 *bulk pull* analysis), not `a1_bureau_fill/summary.md`.

## Context
- VS Code, window title `retail.collections.risk_profiling [Dev Container: cdp-devcontainer:latest @ 10.119.132.99]`.
- Tabs: `pipeline_registry.py`, `summary.md` (marked **M** = modified, tracked; handoff 2's file was **U** = untracked).
- Breadcrumb: `tmp_validation > a1_bulk_pull > summary.md > # A1 bulk pull: summary (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus)`
- Git blame on line 1: "You, 3 hours ago • A1 bulk pull: snippet to measure r[cut off]"; first photo also shows "You, 22 seconds ago | 1 author (You)".
- Bottom bar in the last photo shows branch `persona_refactor*` (the `feature/` prefix is cut off).
- The photos overlap (L1-58, L56-112, L109-165, L157-195), so I merged them into one continuous file, 195 lines in all. Word wrap is on and I omitted line numbers.
- I was sent IMG_9017-9020 only; the file looks complete (ends at line 195, blank).

---

## `tmp_validation/a1_bulk_pull/summary.md`

````markdown
# A1 bulk pull: summary (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus)

**Status: final.** PROD results are in for all four model_ids (`results_<model_id>.md`, no part failed, check 0 PASS). Code read: DE branch `origin/bureau-pipeline-analysis` @ `1fd13b41`; file:line below are on that branch. Two commits landed on that branch during the read (`a050e3a6`, `1fd13b41`: mongo CIF resolution in `prm_bureau.py`, `_scope.py`); neither touches the salary formula.

## 1. DE code, per source

`feat_bureau_salary_unified.py` unions three intermediate tables and keeps one row per `(cif_id, salary_month_end)`.

- **`alert`** (rank 1, `feat_bureau_salary_unified.py:52`)
  - Tables: `int_bureau_alert_salary_monthly` <- `prm_bureau_alert_enriched` <- `stg_aecb_alert` <- `sa_ops_aecb_alert`.
  - Amount: `salary_credit_amount` of 4 alert types (`avaregesalarychanged`, `salaryaccountadded`, `salaryaccountisadded/closed`, `salaryaccountclosed`; `int_bureau_alert_salary_monthly.py:21-27, 42`); NULL amounts dropped.
  - Date: `salary_month_end` = `last_day(extract_date)` (`:48`); one row per CIF-month: latest `extract_date`, then the larger amount (`:50-55`).
- **`salary_credit`** (rank 2, `feat_bureau_salary_unified.py:60`)
  - Tables: `int_bureau_salary_credit_monthly` <- `prm_bureau_salary_history` <- `stg_aecb_salary_history` <- `sa_ops_aecb_sub_sal_cr_hist`.
  - Amount: `sum(subj_salcr_hist_tot_sal_amt)` over providers (`int_bureau_salary_credit_monthly.py:38`); the grain adds file id and record id.
  - Date: `salary_month_end` = `last_day(to_date(subj_salcr_hist_ref_mnth, "MMyyyy"))` (`:35`).
- **`bureau_salary`** (rank 3, `feat_bureau_salary_unified.py:68`)
  - Tables: `int_bureau_salary_monthly` <- `prm_bureau_subj_charac` <- `stg_aecb_subj_charac` <- `sa_ops_aecb_subj_charac`.
  - Amount: `subj_charac_val` of codes 232/233/234/235 pivoted to `sal_1m/3m/6m/12m` (`stg_aecb_subj_charac.py:43,68`; `prm_bureau.py:424-429, 533-534`, `F.max` per record).
  - Date: `salary_month_end` = `last_day(add_months(EDP_LOAD_DATE, -back))`, back = 1..12 (`int_bureau_salary_monthly.py:64`).

**Precedence** (`feat_bureau_salary_unified.py:78-84`), per `(cif_id, salary_month_end)`, in this order: (1) a usable amount (non-null and non-zero) first; (2) then 0 over NULL; (3) then the source rank (alert < salary_credit < bureau_salary); (4) then the latest load date (alert: `extract_date`; pull: `EDP_LOAD_DATE`; credit: none); (5) then the larger amount. A pull month is therefore shown only where no alert / credit row has a usable amount for that CIF-month (an alert 0 or NULL loses to a usable pull amount). The output is restricted to the spine CIFs (`:85-92`); staging scopes at bureau-file level, a superset.

**`bureau_salary` columns read:** `sal_1m`, `sal_3m`, `sal_6m`, `sal_12m` (codes 232-235) and `EDP_LOAD_DATE` (the "pull date", treated as "today"); `subj_charac_hdr_file_id`, `subj_charac_rec_id`, `source_identifier` and `cif_id` for keys and CIF resolution. No other aggregate column is read.

**Exact monthly formula** (`int_bureau_salary_monthly.py:35-46, 60-73`): four bands, even split of the nested difference, floored at 0:

```python
_BANDS = [(range(1, 2), "sal_1m", None, 1), (range(2, 4), "sal_3m", "sal_1m", 2),
          (range(4, 7), "sal_6m", "sal_3m", 3), (range(7, 13), "sal_12m", "sal_6m", 6)]    # :35-40
total = F.col(outer) if inner is None else F.col(outer) - F.col(inner)                    # :45
return F.when(total.isNotNull(), F.greatest(total / n_months, F.lit(0.0)))                # :46
# month = last_day(add_months(EDP_LOAD_DATE, -back))                                        # :64
```

(In the photo the right-hand comments are `# :35-40`, `# :45`, `# :46`, `# :64`, staggered down the right edge; the exact alignment of `:45`/`:46` to lines is my reading.)

So for a pull loaded in month t: month t-1 = `A1`; months t-2, t-3 = `(A3-A1)/2` each; t-4..t-6 = `(A6-A3)/3`; t-7..t-12 = `(A12-A6)/6`. It goes back 12 months, ending at the previous calendar month; the DE reads 232-235 as nested "last N months" totals (the codes are not documented in the repo: to confirm with the DE, section 5).

- **NULL:** a missing `A1` makes months t-1..t-3 NULL (bands 0 and 1 both use it); a missing `A3` makes t-2..t-6 NULL; a missing `A6` makes t-4..t-12 NULL; a missing `A12` makes t-7..t-12 NULL. The NULL months are rows with a NULL amount.
- **0 / negative:** a negative difference (outer smaller than the nested total) gives 0 for that band: the pull's totals are not met and nothing flags it. A zero total gives 0 months.
- **Two pulls with overlapping windows:** both produce rows for the same CIF-month; `int_bureau_salary_monthly` keeps both (grain includes record and load date); the unified step keeps one: the usable amount, then the latest `EDP_LOAD_DATE`. No reconciliation: a later pull's `A1` (which pins its previous month exactly) is not used to correct the earlier pull's guess.

**Things that look wrong or risky**

1. **No filter on `source_identifier`** (`prm_bureau.py:508-511` shows it takes `bulk` and `mongo`): `bureau_salary` is every record carrying codes 232-235, bulk pull and on-demand (mongo) responses alike. Part 1a splits coverage by source.
2. **`EDP_LOAD_DATE` is an ETL load stamp, not a pull date** (the DE's own comment, `stg_aecb_subj_charac.py:34`, T35). All 12 months are anchored to it ("today" = load date): a load that lags the real pull shifts every month.
3. **Mongo one-to-many** (`prm_bureau.py:471-478`): a record is repeated for every CIF mapped to its file, so one salary can attach to several CIFs.
4. **"Usable first" beats "latest load"** (`feat_bureau_salary_unified.py:79-82`): a later pull that says 0 (salary stopped) loses to an earlier pull's positive amount for the same month, and an alert 0 loses to any positive pull amount. Stops are the hardest thing to see; this rule hides them. Part 3 counts the stops the inferred series misses.
5. **Silent floor at 0** (`:46`): inconsistent totals (nesting violated) become 0 months instead of a flag; part 2 counts them.

## 2. Coverage - verdict: about 1%, not 5%, and the precedence is not the reason

PROD run 2026-11-12, all four model_ids, no part failed. **Check 0 PASSES in all four**: our replica of the DE formula equals `int_bureau_salary_monthly` row for row (0 differences in 7,764 / 1,908 / 1,200 / 456 rows) and the unified table of the pull CIFs is reproduced exactly by the DE precedence, so everything below describes the DE's real output.

| | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| raw pull records / CIFs (spine) | 647 / 646 | 159 / 159 | 100 / 100 | 38 / 38 |
| % of latest-month obs base CIFs | 0.8% | 1.4% | 0.03% | 0.1% |
| % of Jan-May 2026 obs base CIFs | 1.6% | 2.0% | 0.03% | <0.1% |
| CIFs A1 would see (a pull month in W) | 154 (0.8%) | 52 (1.4%) | 84 (0.03%) | 37 (0.1%) |
| `source_identifier` | all `bulk` | all `bulk` | all `bulk` | all `bulk` |
| load months / distinct `EDP_LOAD_DATE` | 2026-09 only / 2 | 2026-09 / 1 | 2026-09 / 1 | 2026-09 / 1 |
| CIFs pulled more than once | <10 | 0 | 0 | 0 |
| raw pull months shown as `bureau_salary` | 82.5% | 89.8% | 85.9% | 87.3% |
| hidden by `alert` / `salary_credit` | 17.0% / 0.5% | 10.1% / <10 | 14.1% / 0 | 12.7% / 0 |

- **The ~5% is not in the data.** The raw table holds about 650 pull records for cc_60_180 (0.8% of the obs base) and 159 for rl_60_180 (1.4%); 180+ is 0.03-0.1%. The unified output shows 0.1-1.4% because the raw pull itself is that small; precedence hides only 10-17% of pull months (nearly all behind `alert`; `salary_credit` is negligible).
- **It is one snapshot, not a schedule:** one load month (2026-09) and, with one exception, one pull per CIF, so there are no gaps to measure and no later pull to pin months. The 12 CIF-months inferred by two pulls agree within 5%.
- **No on-demand (mongo) rows** reach the spine in any model_id, so the missing `source_identifier` filter is harmless today.
- **Not measurable from these files:** records dropped before they get here. The snippet reads spine CIFs with a resolved `cif_id` only. If the pull really covered ~5% of customers, the gap sits in CIF resolution or file-level scope in `prm_bureau_subj_charac` (see section 5, question 2).

## 3. Spreading and truth test - verdict: the inferred pull often sits well below internal salary

**Spreading.** All four totals are present in every record and **no band sum is negative** in any model_id, so the cumulative (nested) reading of codes 232-235 holds in the data. 84-90% of records vary across bands in 60_180 / 180+ (flat: 13.8%, 10.7%, 16.0%, <10); 10-12% have a 12-month total of 0 (all twelve months 0).

**Pull vs internal salary** (flat spread, CIF-months of pull CIFs with internal salary):

| | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| CIFs / CIF-months | 323 / 1,652 | 129 / 586 | 58 / 340 | 31 / 74 |
| within 5% | 32.7% | 27.0% | 37.9% | 24.3% |
| pull higher (> 5%) | 23.2% | 24.7% | 27.4% | 31.1% |
| lower 5-25% | 15.9% | 14.2% | 15.6% | 16.2% |
| **lower by > 25%** | **28.2%** | **34.1%** | **19.1%** | **28.4%** |
| CIFs with 3+ months lower by > 25% | 83 (26%) | 33 (26%) | 11 (19%) | <10 |
| internal level change: pull stays flat | 79.4% | 82.4% | 83.1% | 100% (13 events) |
| internal stop: pull stays flat | 78.2% | 77.3% | <10 events | 87.5% (16 events) |

A cross-bank pull should match internal or exceed it; instead it is clearly below in 19-34% of CIF-months, and about a quarter of the CIFs are below by more than 25% for three or more months. Four in five internal level changes and stops are not seen by the flat spread. Plausible causes (not separable with these files): months anchored to the load stamp instead of the pull date; a different measure behind 232-235; salary paid here and not counted there. A shift test would tell the first apart.

## 4. Rebuild - verdict: no better on level, better on stops, almost no effect on A1

Rule: `README.md` ("The alert-shaped rebuild"). It applies to the pull records with a salary alert in their 12 months.

| | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| records with an alert in the window | 363 (56%) | 68 (43%) | 53 (53%) | 20 (53%) |
| no alert (rebuild = flat spread) | 284 | 91 | 47 | 18 |
| exact fit | 56.5% | 51.5% | 69.8% | 60% |
| **conflict** (`band_split`) | **43.5%** | **48.5%** | **30.2%** | <10 |
| `flat_fallback` | 0 | 0 | 0 | 0 |
| CIF-months moved > 5% / > 25% vs flat | 26.0% / 14.2% | 16.0% / 8.8% | 23.2% / 14.1% | 22.4% / 11.4% |

Flat vs rebuild on the truth test (all pull CIFs with internal salary; lower is better for "lower > 25%" and "stays flat"):

| | cc_60_180 | rl_60_180 | cc_180_plus |
|---|---|---|---|
| within 5% | 32.7% -> 32.0% | 27.0% -> 25.3% | 37.9% -> 38.8% |
| lower by > 25% | 28.2% -> 29.3% | 34.1% -> 36.2% | 19.1% -> 20.3% |
| stop: pull stays flat | 78.2% -> 70.9% | 77.3% -> 75.0% | - |
| level change: pull stays flat | 79.4% -> 78.2% | 82.4% -> 81.5% | 83.1% -> 83.1% |

Only the pull CIFs with an alert in the window (cc_60_180, 122 CIFs): within 5% 28.1% -> 24.7%, lower by > 25% 28.6% -> 33.6%, but stops missed 86.2% -> 67.7% and level changes missed 87.7% -> 80.7%. rl_60_180 (48 CIFs): within 5% 21.2% -> 13.9%, lower > 25% 34.3% -> 43.1%, stops missed 78.6% -> 71.4%. 180+ cells are too small to read.

- **The rebuild reacts to alerts (more stops and changes seen) but the levels it lands on agree with internal salary no better, and worse where alerts exist.** Conflicts are frequent (30-48%): the alert month and the totals often disagree about when the level changed, which fits alerts that lag the real change.
- **A1 effect: negligible.** Latest-month rows of pull CIFs: 161 / 56 / 87 / 38 (of 19,292 / 3,985 / 318,663 / 55,371 rows). Income level changes for fewer than 10 rows in cc_60_180 and for 0 in the other three (the engine's own `income_level`, carry kept). With 0.03-1.4% coverage there is little to change.
- **Recommendation:** do not adopt the rebuild now. Keep the flat spread; revisit when pulls repeat (a later pull's `A1`/`A3` pins months) and once the month anchoring is checked.

## 5. Questions for the DE and design note

**Questions**

1. What do codes 232-235 mean exactly (cumulative "last N months" including the nested window?), and is there a documented reference date for the look-back (the response date, not the load date)?
2. The raw table holds ~650 spine pull records (cc_60_180), 0.8% of the obs base, not ~5%: how many records does `sa_ops_aecb_subj_charac` hold for 232-235 in total, how many lose their `cif_id` in `prm_bureau_subj_charac`, and how many fall outside the file-level scope? What is the real pull date / response date per record, and where is it (`sa_ops_aecb_sub_basic_dtl`, header)? What is the schedule of the bulk pull, and which populations (all 61-180? only some products)? Why do `bureau_salary` months stop at 2026-08 (is that one load around 2026-09)?
3. Is mixing `mongo` (on-demand) responses into `bureau_salary` intended?
4. Can a record map to several CIFs on purpose (joint accounts)? Should the salary be shared?
5. Should a later pull's 0 beat an earlier pull's positive amount (a stop)?

**Design note (not code)**

- Keep the pull rows' provenance in the unified table: `source_identifier`, record load date, and the band the month came from.
- Replace the flat spread with a band-sum-preserving, alert-aware inference (the rebuild here) until a pull exists every ~2 months; then reconcile overlapping pulls (a later pull's `A1`/`A3` pin months the earlier one only guessed).
- Order the within-source rule by latest pull first, so a stop is not hidden by an older positive amount.
- Flag floored (negative-difference) bands instead of silently returning 0.

**Cleanup:** after the results are pasted back, delete `tmp_validation/a1_bulk_pull/`. The DE catalog entries merged into `catalog_outputs.yml` (staging, primary, intermediate bureau salary tables) stay.
````

---

## Notes
- The photos are angled and slightly blurred. Please check dense numbers against the file. The least certain are the section 2 table (the `<10` and `0` cells and the hidden-by percentages), the section 3 table (rl_180_plus and cc_180_plus small cells), and the section 4 tables.
- The commit hashes `1fd13b41` and `a050e3a6`, and the file:line references (e.g. `:21-27, 42`, `:424-429, 533-534`), are as read from the photos.
- The photos can't be saved as images from chat; this is the text transcription only.
