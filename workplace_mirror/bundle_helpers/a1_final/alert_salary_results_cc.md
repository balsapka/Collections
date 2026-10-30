# Handoff 19: `tmp_validation/a1_alert_salary/summary.md` (photos 77-79), 2026-10-30

## Context for Claude Code
- Source: 3 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-10-30 ~09:37 Dubai. Tabs: `pipeline_registry.py`, `summary.md` (U = untracked, active). Path: `tmp_validation > a1_alert_salary > summary.md`. Status bar: Ln 1, Col 1, Spaces: 4, Markdown.
- Title: "A1 alert salary - summary (CC `cc_60_180`; RL pending)". Hypotheses H0-H6, L and M for using the AECB alert table's `salary_credit_amount` as A1's bureau salary source. Follows handoffs 1-18; relates to the bureau join work in handoffs 3, 12 and 18.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and `results_cc_60_180.json`.
- Photos overlap and are merged into source lines 1-27. Photo-to-line map: photo 77 = lines 1-13 (taken first in time, 9:36); photo 78 = lines 1, 11-26; photo 79 = lines 1, 17, 20-27. The chat order was 20-27, 11-26, 1-13.
- Lines 3 to 15 are single long source lines (soft-wrapped in the editor). They are kept as one paragraph per source line below. Table rows (lines 5-15) are markdown table rows.
- The Mac link was disconnected when this was written, so this file was written in the cloud workspace and sent to chat. Copy it to `~/Python/Collections/pics/claude_code_handoff_19.md`.

---

## `summary.md` (lines 1-27)

````
1   # A1 alert salary - summary (CC `cc_60_180`; RL pending)
2
3   **RL is missing:** `results_rl_60_180.json` is not on the branch, so every RL cell is *pending*. CC base: 19,292 accounts / 18,725 CIFs, observation 2026-08-31, W = Jun-Aug 2026. Not loaded in the sandpit (so skipped in L/M): `sub_basic_dtl`, `subj_link`, `res_hdr_trail`, `req_indv`, `cntrct_smry`, `emplnt_hist`, `oth_incm`, `charac`, `subj_hist`, `addr_hist`, `ec_ops_aecb_alert_dly_smry`, `sa_aecb_alerts`. `stg_contract_detail` and `*_consolidated_summary` loaded **empty**. Internal salary = decoded `wm_fea_salary_days_since_increment` (`feat_cif_internal_salary_monthly` does not exist).
4
5   | Hyp | Verdict (CC) | Key numbers (CC \| RL pending) |
6   |---|---|---|
7   | H0 inputs | **CONFIRMED** usable column | 2.84M rows, 80.9k CIFs, 2022-01..2026-08. `salary_credit_amount` positive on 14.9% of rows (13.9% base); positives p10/50/90/99 = 3,000 / 6,767 / 20,266 / 78,488. 10,250 base CIFs (55%) ever have one. `cif_id`=numeric `PRVDR_SUBJ_NUM`, amount = raw `SALARY_CRED_AMT`, untransformed (`prm_bureau.py:157-160`; scope-limited at `stg_aecb_alert.py:112-118`) |
8   | H1 meaning | **CONFIRMED: an AECB *average salary level* sent on salary events, not a month's credit and not our last credit** | Only alert_category 5 ("Account Specific") carries it: type 31 "Average salary changed" (333k rows, 43k CIFs, 78% filled), 32 "Salary account added" (97% filled) and "...added/closed" (48%), 43 "closed" (0.8%). Per CIF: 4 distinct amounts (p50), 11 (p90); 28% of consecutive pulls repeat the amount; 89% of CIFs change amount month to month. No other column is a salary month/date; `OPN_DT` is 52% filled on salary rows, median 706 days before extract (looks like the salary-account open date; not usable) |
9   | H2 dating | **UNCLEAR** | `edp_load_date` = `extract_date` exactly (p10/50/90 = 0) - adds nothing. Salary rows: 1 pull per CIF-month (p50 and p90). Lag vs internal new amount: only 233 of 44,333 alert new-amount events matched an internal one; lag flat from -6 to +6, median 0 - too few and no pattern |
10  | H3 own bank | **REJECTED** as "just our own credit echoed back"; provider split **impossible** | `provider_code` has one value ("026") on all rows; `ref_ops_aecb` has no provider rows, so "026 = ENBD" is unverified. Alert = internal within 2% in the same month for only 13% (shift 0) / 19% (shift 1) of 917 / 1,002 CIF-months; 3,760 CIFs have an alert salary and no internal salary at all in W |
11  | H4 coverage | **CONFIRMED: alert is the only bureau path that reaches CIFs** | Base CIFs with salary ≥1,000: alert W 3,795 (20.3%), 6m 6,054, 12m 8,045, ever 10,212 · internal W 425, 12m 6,907 · today's bureau path W **0**, 12m 17, ever 51 (0.27%). Alert W with no internal W: 3,760. No internal in 12m (11,817 CIFs): 6,559 (56%) have an alert ≥1,000 in 12m. Shift 1: alert W 2,868 |
12  | H5 agreement | **REJECTED** (alert ≠ internal monthly salary); month **UNCLEAR** | 917 CIF-months / 617 CIFs: alert/internal p10/50/90 = 0.30 / 1.00 / 3.33; within 10% 22% (shift 0) vs 28% (shift 1); within 2% 13% / 19%. Shift 1 fits "salary account added" better (39% vs 24% within 10%), worse for type 31 (18% vs 21%) |
13  | H6 A1 impact | **CONFIRMED material** | 18,300 CIFs (18,852 rows) have internal <1,000 in every month of W. Of them, alert ≥1,000 in W: 3,760 CIFs / 3,857 accounts (20.5%); W total ≥6,000: 2,715 / 2,794. Shift 1: 2,839 / 1,946 CIFs. Type 31 alone: 2,997 / 2,233; "added": 1,108 / 656 |
14  | L link | **REJECTED** (no better route found) | The salary-history table has no subject column. Only `contract_link` (`bureau_file_id` + `cb_subject_id`) sits beside a file id: 65 base CIFs (0.35%) reach a salary file through all alert subject pairs vs 51 (0.27%) via today's bridge. Bottleneck: 2.38M salary files vs 162k `contract_link` files. The other candidate (`sub_basic_dtl`) did not load |
15  | M master? | **REJECTED — TRIGGER FEED** | see Recommendation |
16
17  ## Recommendation
18  **Yes: `salary_credit_amount` can be A1's main bureau salary source**, replacing the file-id path, which adds nothing in W (0 CIFs). Filters and month:
19  - **Alert types:** category 5, types **31** (Average salary changed) and **32** (Salary account added; Salary account is added/closed). Leave **43** (account closed, ~100 base CIFs, mostly empty) out. Provider: nothing to filter (single code 026).
20  - **Month:** use the **extract month** (shift 0, `extract_date ≤ observation date`). Shift 1 is not supported by the evidence (H2/H5 unclear).
21  - **Meaning:** treat it as the reported salary *level* at the pull, not a month's credit. Rows are events, so a missing month is not zero: 20% of CIFs have one in W but 43% in 12m. Two decisions for you, not applied: carry the last level forward (e.g. up to 12m), and whether the "W total ≥ 2x threshold" sum is right for a level (one 7,000 row in three months reads as 7,000, not 21,000).
22  - **Caveats:** the internal series looks thin in W (425 CIFs vs 3,424 in 6m); check the WM snapshot date before trusting H2/H5 overlap. The amount may be stale for customers whose job ended.
23
24  **L:** no cheaper link exists in what loaded; the problem is file-id coverage (0.27-0.35%), so go around it with `cif_id`.
25
26  **M verdict: TRIGGER FEED.** (1) File ids never match: 0% overlap, both directions, between every table's file ids (salary history, credit score, contract link/history/detail, court case, payment order) and every alert id column. (2) Only subject id is shared, and not as a superset: 53% of sampled `contract_link` subjects are in the alert table, 2% of alert subjects are in `contract_link`. `cb_trig_id` matches *contract* ids (50% of `contract_link`, 44% of detail, 40% of history contract ids), so alert rows point at contracts, not files. (3) Population: 40-61% of base CIFs have an alert row in a given month (not ~100%), ~30 extract dates a month. (4) Values: alert salary equals the salary-history amount within 2% for 5-8% of 108-118 CIF-months (20 CIFs); exact amount found for 4.5%. (5) Lineage: no code or doc says the alert is built from or feeds the other tables; the daily summary could not be loaded to reconcile. Limits: M4 rests on 109 bridged CIFs, contract values could not be tested (the enriched table has no contract key; `cb_trig_id` is the candidate), and M1/M2 samples are first rows. **Meaning for linking:** the alert table cannot link bureau files to customers; use its own `cif_id`.
27
````

## Notes on specific spots
- Line 3: CC base is stated as 18,725 CIFs here, while other handoffs (3, 7, 12, 13) give 18,731 CIFs for `cc_60_180`. Copied as it appears; the difference may be a genuine dedup or a misread digit.
- Line 7: `prm_bureau.py:157-160` and `stg_aecb_alert.py:112-118` are file:line references; digits are OCR-risk.
- Line 8: the middle quoted phrase `"...added/closed"` is shown in the photo with an ellipsis-like start; read as "Salary account is added/closed".
- Line 11: "alert W 3," wraps onto "795 (20.3%)" in the editor; joined as 3,795.
- Lines 12-13: the shift 0 / shift 1 numbers are dense; verify.
- Line 22: "425 CIFs vs 3,424 in 6m" is read as written.
- The terminal panel and taskbar are not transcribed. The Windows taskbar clock in the photos shows 10/30/2026 ~9:36-9:37.
