# B24 check results (handoff 8, 2026-11-12) — review

**Verdict: passes. Step 8 and the cleanup can go ahead.** The totals in the transcription add up: the move tables sum to the row counts in all four model_ids.

**Products (cc_60_180):** as expected.
- `deposit`: the 95,507 rows only in the old table are all the NULL-balance term-deposit holders the bundle drops.
- `card`: 41 rows only in the new table, and none differ in value. The card logic is the same as bundle 21's, so these are billing rows loaded after bundle 21's table was built (the raw tables keep loading).
- **A1 inputs:** `current` differs in 43,466 customer-months. These are the customer-months whose only row was a dropped deposit row: old `xp_current` 0, new no row. A1 fills both with 0 (`fillna(0)` in `build_cross_product_signals`), so A1 does not change. The check's NULL-vs-0 comparison overstated this. `instalment` 39 and `holding` 41 are the 41 new card rows. Assets: 0.

**Bureau swap:**
- The unified table adds 19% CIF-months (cc_60_180; 4–25% elsewhere); 90–99.6% of rows are alerts.
- Zero rows rise in 60_180 (cc 5,757 → 8,067). These are the DE's 0-amount alerts (`salaryaccountisadded/closed` with 0, which the old node skipped; a stop under the user's closure rule) and pull months of 0.
- Bureau evidence in W gained / lost: cc_60_180 254 / 39 rows; at most 0.9% elsewhere.

**A1 state:**

| | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---|---|---|---|
| rows that change state | 669 (3.5%) | 2,959 (0.9%) | 63 (1.6%) | 293 (0.5%) |
| Moderate, old → new | 14.8% → 13.9% | 6.2% → 6.0% | 8.7% → 8.8% | 3.5% → 3.5% |
| Low, old → new | 25.6% → 27.3% | 8.4% → 8.6% | 49.2% → 49.3% | 11.0% → 11.0% |
| Unknown, old → new | 58.0% → 57.2% | 85.2% → 85.1% | 41.0% → 40.7% | 85.4% → 85.4% |

- cc_60_180 moves net down: Moderate → Low 324 vs Low → Moderate 123, driven by income Stable → Weak 372 vs Weak → Stable 125. The likely cause is the new 0 rows inside the window (a stop ends the carry and leaves a 0 month), plus different alert amounts (987 CIF-months more than 1% apart). The check does not split these causes. This is by construction of the swap and the closure rule the user decided, not a defect.
- RL losing the loan salary costs little: bureau evidence lost (1 → 0) in 10 rl_60_180 rows and 12 rl_180_plus rows.
- High is unchanged (1.6% / 0.3% / 1.2% / 0.1%).

---

# Handoff 8: `tmp_validation/a1_check_final/summary.md` (L1-130)

Source: 3 phone photos (IMG_9043, IMG_9044, IMG_9045) of VS Code, workspace `retail.collections.risk_profiling` [Dev Container: cdp-devcontainer:latest]. Open tabs: `pipeline_registry.py`, `primary.py`, `24_a1_product_primaries_bureau_swap.md`, `summary.md` (marked U = untracked). Breadcrumb: tmp_validation > a1_check_final > summary.md.

Photos overlap (L1-59, L52-112, L89-130) and are merged below into one continuous file. Content is transcribed verbatim. Markdown table separator rows are normalised. Column headers appear as `r1_...` on screen (monospace font); written here as `rl_...` to match the model IDs `rl_60_180` and `rl_180_plus`.

Related: earlier handoffs 2, 3 and 5 cover the `a1_bureau_fill`, `a1_bulk_pull` and baseline summaries. Handoff 4 is the failed apply log (ImportError on `_cif`). This `a1_check_final` run is the old-vs-new comparison for the B24 bureau swap (bundle `24_a1_product_primaries_bureau_swap.md`). Whether it was produced before or after the failed apply is not visible in the photos.

---

```markdown
# A1 check final

Latest month 2026-08-31. Cells show n (% of rows). Pairs read old→new.

---

## B24 PRODUCTS (cc_60_180)

| product | old | new | only old | only old (null bal) | only new | differ bal/cur/inst |
|---|---:|---:|---:|---:|---:|---:|
| card | 66,013,090 | 66,013,131 | 0 | 0 | 41 | 0/0/0 |
| deposit | 1,800,735 | 1,705,228 | 95,507 | 95,507 | 0 | 0/0/0 |
| investment | 1,528,125 | 1,528,125 | 0 | 0 | 0 | 0/0/0 |
| loan | 4,907,414 | 4,907,414 | 0 | 0 | 0 | 0/0/0 |
| wm | 648,132 | 648,132 | 0 | 0 | 0 | 0/0/0 |

## B24 A1 INPUTS (cc_60_180)

| metric | value |
|---|---:|
| customer-months | 58,151,523 |
| any input differs | 43,466 |
| latest month customer-months | 3,070,842 |
| latest month differ | 1,957 |
| differ by input: assets | 0 |
| differ by input: instalment | 39 |
| differ by input: current | 43,466 |
| differ by input: holding | 41 |

---

## B24 BUREAU

| metric | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| CIF-months old | 24,887 | 207,056 | 2,876 | 20,415 |
| of which zero | 5,757 | 36,194 | 662 | 3,912 |
| CIF-months new | 29,564 | 220,621 | 3,607 | 21,982 |
| of which zero | 8,067 | 35,497 | 986 | 3,693 |
| only old | 1,667 | 10,554 | 215 | 1,181 |
| only new | 6,344 | 24,119 | 946 | 2,748 |
| in both, > 1% apart | 987 | 8,854 | 128 | 1,057 |

New by salary_source:

| salary_source | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| alert | 28,522 (96.5%) | 219,711 (99.6%) | 3,258 (90.3%) | 21,588 (98.2%) |
| bureau_salary | 928 (3.1%) | 851 (0.4%) | 329 (9.1%) | 387 (1.8%) |
| salary_credit | 114 (0.4%) | 59 (0.0%) | 20 (0.6%) | 7 (0.0%) |

## B24 INCOME

Bureau evidence in W (>= AED 1,000):

| old→new | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| 0→0 | 14,461 (75.0%) | 287,115 (90.1%) | 3,382 (84.9%) | 52,127 (94.1%) |
| 0→1 | 254 (1.3%) | 523 (0.2%) | 36 (0.9%) | 73 (0.1%) |
| 1→0 | 39 (0.2%) | 74 (0.0%) | 10 (0.3%) | 12 (0.0%) |
| 1→1 | 4,538 (23.5%) | 30,951 (9.7%) | 557 (14.0%) | 3,159 (5.7%) |

Income source:

| old→new | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| both→both | 41 (0.2%) | 102 (0.0%) | 21 (0.5%) | 26 (0.0%) |
| both→internal | - | - | - | 1 (0.0%) |
| bureau→bureau | 4,497 (23.3%) | 30,849 (9.7%) | 536 (13.5%) | 3,133 (5.7%) |
| bureau→none | 39 (0.2%) | 74 (0.0%) | 10 (0.3%) | 11 (0.0%) |
| internal→both | 23 (0.1%) | 23 (0.0%) | 7 (0.2%) | 1 (0.0%) |
| internal→internal | 376 (1.9%) | 488 (0.2%) | 177 (4.4%) | 121 (0.2%) |
| none→bureau | 231 (1.2%) | 500 (0.2%) | 29 (0.7%) | 72 (0.1%) |
| none→none | 14,085 (73.0%) | 286,627 (89.9%) | 3,205 (80.4%) | 52,006 (93.9%) |

Income level:

| old→new | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| none→none | 14,085 (73.0%) | 286,627 (89.9%) | 3,205 (80.4%) | 52,006 (93.9%) |
| none→stable | 81 (0.4%) | 164 (0.1%) | 10 (0.3%) | 24 (0.0%) |
| none→weak | 150 (0.8%) | 336 (0.1%) | 19 (0.5%) | 48 (0.1%) |
| stable→none | 29 (0.2%) | 44 (0.0%) | 3 (0.1%) | 4 (0.0%) |
| stable→stable | 2,595 (13.5%) | 19,587 (6.1%) | 337 (8.5%) | 1,837 (3.3%) |
| stable→weak | 372 (1.9%) | 1,606 (0.5%) | 31 (0.8%) | 153 (0.3%) |
| weak→none | 10 (0.1%) | 30 (0.0%) | 7 (0.2%) | 7 (0.0%) |
| weak→stable | 125 (0.6%) | 1,155 (0.4%) | 23 (0.6%) | 139 (0.3%) |
| weak→weak | 1,845 (9.6%) | 9,114 (2.9%) | 350 (8.8%) | 1,153 (2.1%) |

## B24 A1 OUTPUT

| rows (new) | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
|  | 19,292 | 318,663 | 3,985 | 55,371 |

New state:

| state | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| high | 312 (1.6%) | 845 (0.3%) | 47 (1.2%) | 66 (0.1%) |
| low | 5,263 (27.3%) | 27,470 (8.6%) | 1,965 (49.3%) | 6,115 (11.0%) |
| moderate | 2,681 (13.9%) | 19,268 (6.0%) | 351 (8.8%) | 1,914 (3.5%) |
| unknown | 11,036 (57.2%) | 271,080 (85.1%) | 1,622 (40.7%) | 47,276 (85.4%) |

Old state:

| state | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| high | 311 (1.6%) | 836 (0.3%) | 47 (1.2%) | 66 (0.1%) |
| low | 4,948 (25.6%) | 26,789 (8.4%) | 1,960 (49.2%) | 6,077 (11.0%) |
| moderate | 2,850 (14.8%) | 19,623 (6.2%) | 345 (8.7%) | 1,919 (3.5%) |
| unknown | 11,183 (58.0%) | 271,415 (85.2%) | 1,633 (41.0%) | 47,309 (85.4%) |

## B24 A1 MOVES

| old→new | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---:|---:|---:|---:|
| high→high | 303 (1.6%) | 829 (0.3%) | 47 (1.2%) | 64 (0.1%) |
| high→moderate | 8 (0.0%) | 7 (0.0%) | - | 2 (0.0%) |
| low→low | 4,817 (25.0%) | 25,744 (8.1%) | 1,934 (48.5%) | 5,961 (10.8%) |
| low→moderate | 123 (0.6%) | 1,018 (0.3%) | 24 (0.6%) | 113 (0.2%) |
| low→unknown | 8 (0.0%) | 27 (0.0%) | 2 (0.1%) | 3 (0.0%) |
| moderate→high | 9 (0.0%) | 16 (0.0%) | - | 2 (0.0%) |
| moderate→low | 324 (1.7%) | 1,445 (0.5%) | 22 (0.6%) | 129 (0.2%) |
| moderate→moderate | 2,496 (12.9%) | 18,120 (5.7%) | 322 (8.1%) | 1,784 (3.2%) |
| moderate→unknown | 21 (0.1%) | 42 (0.0%) | 1 (0.0%) | 4 (0.0%) |
| unknown→low | 122 (0.6%) | 281 (0.1%) | 9 (0.2%) | 25 (0.0%) |
| unknown→moderate | 54 (0.3%) | 123 (0.0%) | 5 (0.1%) | 15 (0.0%) |
| unknown→unknown | 11,007 (57.1%) | 271,011 (85.0%) | 1,619 (40.6%) | 47,269 (85.4%) |
```

(File ends at L129 plus an empty L130.)

---

## Notes

- Consistency checks I ran on the transcription:
  - The cc_60_180 MOVES column sums to 19,292, matching `rows (new)`.
  - cc_60_180 old-state `high` 311 = 303 + 8, matching the moves table.
  - The other three model columns were not summed.
- The MOVES table has 12 rows. Transitions that are absent from it (e.g. `high→low`, `low→high`, `unknown→high`) are simply not listed on screen; I did not add them.
- Least-certain cells (dense or blurry in the photos; check against the source file):
  - `rl_180_plus` column in the INCOME blocks (L58-L88).
  - `rl_60_180` MOVES cells (L118-L129), especially the `-` entries on `high→moderate` and `moderate→high`.
  - Percent figures in L96-L112 (New and Old state).
- `rl_` vs `r1_`: the screen font renders both similarly. I used `rl_` throughout.
- Not visible in any photo: anything after L130 (file ends at the empty L130), and the file's `PRODUCTS` tables for models other than `cc_60_180`.
