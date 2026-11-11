# Handoff 66: `bureau_salary_unified_handover.md` (A1 ability, swap to `feat_bureau_salary_unified`), lines 1-72

## Context for Claude Code

- Source: 3 phone photos of VS Code (Dell laptop), file `tasks/bureau_salary_unified_handover.md`, marked `U` (untracked). Other open tabs: `pipeline_registry.py`, `21_a1_evidence_family_rule.md`, `oos_results.md` (marked `M`). Editor status: Ln 1 Col 1, Spaces: 2, UTF-8, LF. The breadcrumb reads `tasks > bureau_salary_unified_handover.md`.
- Content: a handover note written for another Claude session. It says what the data engineer (DE) delivered, what was done in this repo (catalog entry only), what the A1 (ability) code needs, what to validate on PROD, and what was not verified.
- Photos merged by editor line number: photo 3 = lines 1-36, photo 2 = lines 31-64, photo 1 = lines 47-72. Lines 1-72 are covered. Line 72 is the last line and is empty.
- Format: `NNN  text`, NNN is the editor line number. The file is hard-wrapped, so each editor line is one row. Numbered-list continuation lines are indented 3 spaces, bullet continuation lines 2 spaces, as in the editor.

## Transcription

```
  1  # Handover: replace bureau salary input in A1 (ability) with `feat_bureau_salary_unified`
  2  
  3  Status: **catalog entry added only. No A1 code changed yet.** Nothing was run (no PROD data; no
  4  `kedro run`).
  5  
  6  ## What the DE delivered
  7  - Branch `bureau-pipeline-analysis` (not merged/pulled here). Node:
  8    `nodes/features/bureau/feat_bureau_salary_unified.py`.
  9  - Already run for all four models; one parquet per `model_id` at
 10    `${_project.hdfs_path}/${model_id}/${folders.feat}/bureau/salary_unified`.
 11  - Schema (grain `cif_id x salary_month_end`): `cif_id long`, `salary_month_end date`,
 12    `monthly_salary double`, `salary_source string`.
 13  - Logic: union of three sources, one row per (cif, month). Precedence: `alert` (salary alerts) >
 14    `salary_credit` (bank salary credit history) > `bureau_salary` (AECB salary spread). Usable =
 15    non-null and non-zero; a 0/null in a higher source is filled from the next source. If nothing is
 16    usable, 0 is kept over null. Rows with null cif_id are dropped. Output is scoped to the model's
 17    spine CIFs.
 18  
 19  ## Done in this repo
 20  - `conf/base/catalog/catalog_bureau.yml`: added `feat_bureau_salary_unified` (SparkDataset, parquet,
 21    path above, read-only). YAML parses. `feat_cif_bureau_salary_monthly` was left in place.
 22  - Merge caveat: the DE branch also defines `feat_bureau_salary_unified` in `catalog_outputs.yml`. If
 23    that branch is ever merged, remove one of the two entries (duplicate catalog keys).
 24  
 25  ## What the A1 code needs (for the other session)
 26  Current wiring: `a1_ability/pipeline.py:43` maps `bureau_salary` ->
 27  `feat_cif_bureau_salary_monthly`; `signals.py::build_income_signals` consumes columns `cif_id,
 28  month_end, bureau_salary`.
 29  
 30  1. `pipeline.py`: point `"bureau_salary"` input to `feat_bureau_salary_unified` (same for CC and RL;
 31     shared function).
 32  2. `signals.py::build_income_signals`:
 33     - `require_columns(..., ["cif_id","salary_month_end","monthly_salary"],
 34       "feat_bureau_salary_unified")`.
 35     - Rename on read: `salary_month_end -> month_end`, `monthly_salary -> bureau_salary`, so the rest
 36       stays untouched. Ensure `salary_month_end` is a month-end date (the old series used
 37       `F.last_day`); apply `F.last_day` defensively.
 38  3. **Carry-forward (`_with_next_month`, S14) needs a decision.** It was built for AECB *pulls*
 39     (every ~2 months): a pull counts in its month and the next, and a 0 ends the carry. The unified
 40     series is a monthly series whose `alert` and `salary_credit` rows are real monthly credits, so
 41     carrying them forward would double count and mask a missed salary. Recommended: carry only rows
 42     with `salary_source == "bureau_salary"` (the pull-based source) and use the others as-is. The
 43     simplest option is no carry at all, but that would change the S14 behaviour.
 44  4. **RL `_loan_bureau_salary`** (`aecb_last_salary_credit_amount` from `feature_retail_loans`):
 45     likely redundant now that the unified table is CIF-level and covers the AECB sources. Check
 46     overlap before dropping it; if removed, also drop the `loan_features` input and the `if product
 47     == "rl"` branch in `pipeline.py`.
 48  5. `_shows_evidence` / `INCOME_FLOOR` / `MIN_EVIDENCE_AMT` in `classify.py` work on
 49     `bureau_salary_w`. Keep the name or rename to something source-neutral. The unified series
 50     contains 0 rows, which already count as "no evidence" through `MIN_EVIDENCE_AMT` (1000). Confirm
 51     this still holds for the 0 rows kept over null.
 52  6. Optional: `salary_source` allows reporting which source drove income (could feed A1 reason text).
 53  7. Docs and leftovers: update `a1_ability/README.md` (lines ~24-30 input table: swap the row for
 54     `feat_cif_bureau_salary_monthly`; keep `feat_cif_bureau_bounces_monthly`), the `pipeline.py` and
 55     `signals.py` docstrings, and `docs/context/TASKS.md` if A1 close-out items mention bureau salary.
 56     `pipelines/bureau/salary_bounces.py` still produces `feat_cif_bureau_salary_monthly`; leave it
 57     (the bounces output is still used), but its salary output becomes unused by A1. Whatif scripts in
 58     `tmp_validation/a1_aecb_whatif/` and `tmp_validation/a1_high_whatif/` reference the old dataset
 59     and are historical.
 60  
 61  ## Validation to ask for (user runs on PROD)
 62  - Row counts and `salary_source` mix per model_id; share of obs rows with income evidence before vs
 63    after.
 64  - A1 state distribution diff (old vs new input), especially income-weak / salary-stopped states and
 65    the `bureau` / `both` / `none` evidence-source split.
 66  - Check that the unified `salary_month_end` covers the same months as the obs lookback (`2*W`
 67    months).
 68  
 69  ## Not verified
 70  Schema is as given by the user and read from the DE branch code; I have not seen the actual PROD
 71  parquet.
 72  
```

## Notes on specific spots

- Lines 31-36 and 47-64 each appear in two photos and matched.
- Line 47: the editor font showed `== "r1"` (digit one). Every other mention is `rl` (retail loans, e.g. `rl_60_180`), so I transcribed `"rl"`. Check the source if it matters.
- Line 28 begins with `month_end, bureau_salary`.` after a line break inside a backtick span that opens on line 27. The `cif_id,` ends line 27 and the closing backtick is on line 28. Copied as printed.
- Lines 57-58: "Whatif" is capitalised as printed.
- Line 50: "(1000)" is `MIN_EVIDENCE_AMT`. "contains 0 rows" is the zero-valued rows the DE logic keeps over null (see line 16), not an empty table.
- Line 66: `2*W` is as printed (W is the window length; the obs lookback is 2 times W months).
- Related handoffs: `fill_in.md` and `oos_results.md` are in handoffs 60, 61, 65. This one is about the A1 (ability) bureau salary input and does not reference them.
- Line 72 is empty and is the last line I can see.
