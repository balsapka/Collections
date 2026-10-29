# AECB tables in the sandpit (handoff 18, 2026-10-29)

## Context for Claude Code
- Source: 1 phone photo of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-10-29 ~10:18 Dubai. Active tab `bureau.md` (U = untracked); other tabs: `pipeline_registry.py`, `A3_Payment_Credibility_Stats.txt`, `a2_v04_snippet.py` (U), `a2_b06_cc_check_run_summary_202...` (U). Path: `tmp_validation > a1_bureau_link > bureau.md`.
- Only the table (source lines 1-15) is transcribed, as requested. The terminal panel below it (a Claude Code answer about V1/V2/D1 checks for `a2_v04_snippet.py`) is not transcribed.
- Content: a Spark-style ASCII table listing the AECB (credit bureau) tables in schema `dpl_uae_operations`: record counts, min/max `edp_load_date`, and a partition count. Follows handoffs 1-17; relates to the bureau join work in handoffs 3 and 12 (`prm_bureau_cif_bridge`, `stg_aecb_salary_history`, `prm_bureau_alert_enriched`).
- Transcribed by Claude (chat) from the image, not copied from the file. Verify digits against the real file.
- The last column header is cut off at the right edge of the photo: it reads `total_part` followed by the border, probably `total_partitions`. The right border bars on the data rows are shown as `|`.

## Same table, compact

| table_name | total_records | min_edp_load_date | max_edp_load_date | total_part |
|---|---|---|---|---|
| dpl_uae_operations.ref_ops_aecb | 1496 | 2026-01-22 | 2026-01-22 | 1 |
| dpl_uae_operations.sa_ops_aecb_subj_crdt_score | 5355148 | 2020-11-20 | 2026-10-13 | 2143 |
| dpl_uae_operations.sa_ops_aecb_subj_con_tot_smry | 4674312 | 2023-01-20 | 2026-10-18 | 1358 |
| dpl_uae_operations.sa_ops_aecb_subj_cntrct_hist | 995199660 | 2020-07-04 | 2026-10-12 | 2240 |
| dpl_uae_operations.sa_ops_aecb_subj_cntrct_dtl | 69582242 | 2020-07-04 | 2026-10-19 | 2249 |
| dpl_uae_operations.sa_ops_aecb_sub_sal_cr_hist | 148350290 | 2023-06-23 | 2026-10-13 | 1199 |
| dpl_uae_operations.sa_ops_aecb_subj_cntrct_link | 1299643 | 2020-07-06 | 2026-10-13 | 2154 |
| dpl_uae_operations.sa_ops_aecb_subj_court_case | 78075 | 2023-01-20 | 2026-10-13 | 1312 |
| dpl_uae_operations.sa_ops_aecb_subj_pymnt_order | 1466948 | 2020-07-04 | 2026-10-13 | 2240 |
| dpl_uae_operations.sa_ops_aecb_alert | 89911389 | 2022-01-01 | 2026-10-14 | 1541 |
| dpl_uae_operations.sa_ops_aecb_alert_othprv_sub | 43232489 | 2022-01-01 | 2026-10-14 | 1540 |

## Notes on specific spots
- Table name spelling is as shown, including the irregular `sa_ops_aecb_sub_sal_cr_hist` (row 9, "sub" not "subj") and `sa_ops_aecb_alert_othprv_sub` (row 14). Check these two against the catalog.
- Column widths in the first block are approximate (names in rows 5-14 are wider than the header border in the photo).
- Largest tables: `subj_cntrct_hist` 995,199,660 rows; `sub_sal_cr_hist` 148,350,290; `alert` 89,911,389; `subj_cntrct_dtl` 69,582,242; `alert_othprv_sub` 43,232,489.
- `ref_ops_aecb` is a single snapshot (min = max = 2026-01-22, 1 partition).
