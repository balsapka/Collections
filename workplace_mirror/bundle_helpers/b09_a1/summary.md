**What this bundle does.** A1's bureau salary moves to the AECB alert table (spec S14), and
bundle 08's check and the unused salary-history primary are removed.

- **`feat_cif_bureau_salary_monthly`** now reads `prm_bureau_alert_enriched`, keyed by CIF:
  one row per customer and pull month, the salary on the month's latest pull
  (`extract_date`). Salary rows are `alert_type_number` 31 and 32 with an amount; 43 (salary
  account closed) gives 0. The salary history and `prm_bureau_cif_bridge` reached 0 base CIFs
  in the window, and the bridge can give a co-party's salary (R19).
- **`build_income_signals`**: a pull counts in its own month and the next, never before the
  pull and no further, so pulls every 2 months make a continuous series. RL's
  `feature_retail_loans` salary is carried the same way. S12, the 25% check and "the larger
  of internal and bureau per month" are unchanged; `classify.py` keeps its rules.
- **New diagnostic columns** in `crx_<p>_a1_ability`, which change no state:
  `a1_income_source` (internal, bureau, both, none) and `a1_salary_stopped` (internal salary
  in the prior window, none in the window).
- **Removed**: `b08_check.py`, the `*_a1_ability_b08_check` pipelines and catalog entries,
  `prm_bureau_salary_history` (its node, file and catalog entry; `stg_aecb_salary_history`
  stays). `crx_<p>_a1_ability_v2` stays until this bundle's cleanup as the check's baseline.
- **Check** (`a1_ability/b09_check.py`, pipelines `crx_cc_a1_ability_b09_check`,
  `crx_rl_a1_ability_b09_check`): blocks `B09 OUTPUT`, `REPORT`, `SOURCES` (as in bundle 08,
  with the alert salary as M3) and `AECB`, which shows the state without the alert salary,
  with its pull months, and with the 1-month carry. Bundle 08's `CHANGES` block is gone, so
  run the bundle 08 check for RL **before** applying this bundle if you want its per-change
  attribution.
- Expected for `cc_60_180` (estimates): Unknown about 74% → about 55%; Moderate 1.4% → roughly
  15–18%. RL has not been validated on the alert table yet, so this check is its first read.
