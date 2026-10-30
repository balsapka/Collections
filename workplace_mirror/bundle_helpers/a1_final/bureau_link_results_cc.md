# Handoff 21: `tmp_validation/a1_bureau_link/summary.md` (photos 86-87), 2026-10-30

## Context for Claude Code
- Source: 2 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-10-30 ~13:48 Dubai. Tabs: `pipeline_registry.py`, `summary.md` (active, saved: no U/M marker visible). Path: `tmp_validation > a1_bureau_link > summary.md`. Blame header (photo 2): "You, 5 minutes ago | 1 author (You)"; blame on line 1: "You, 37 minutes ago • A1 bureau link: CC summary, c1 waterfall ..." (cut off).
- Title: "A1 bureau link and CASA / salary sources: CC result". Source is `results_cc_60_180.json`. Follows handoffs 1-20; builds on the bureau work in handoffs 3, 12, 18 and 19 (the alert-salary route is handoff 19).
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and `results_cc_60_180.json`.
- Photos overlap and are merged into source lines 1-77. Photo-to-line map: photo 86 = lines 1, 17, 34-77; photo 87 = lines 1-58. The chat order was 34-77 first, then 1-58.
- Source lines are long soft-wrapped paragraphs. Each is kept on one line below, with no hard breaks inside, except lines 8-13, 14-15 and 18-21, where the editor shows hard-looking wraps as printed.
- The Mac link was disconnected when this was written, so this file was written in the cloud workspace and sent to chat. Copy it to `~/Python/Collections/pics/claude_code_handoff_21.md`.

---

## `summary.md` (lines 1-77)

````
1   # A1 bureau link and CASA / salary sources: CC result
2
3   Base: `cc_60_180`, 31 Aug 2026, 19,292 accounts, 18,724 CIFs. Source: `results_cc_60_180.json` (all 15 tables ran, 0 errors).
4
5   **RL: NOT RUN** (the run took many hours; every RL cell is NOT IN JSON). Counts under 10 are masked as `<10`.
6
7   ## Availability
8   40 of 64 datasets load. Raw AECB that load: crdt_score, con_tot_smry, cntrct_hist, cntrct_dtl, sub_sal_cr_hist,
9   cntrct_link, court_case, pymnt_order, alert, alert_othprv_sub, ref_ops_aecb; also every persisted `stg_aecb_*` /
10  `prm_bureau_*`, `bo_rr_aecb_metric`, WM, comp, `prm_customer_relationship`, `general_acct_mast_bridge`.
11  **NOT AVAILABLE (24):** 21 raw AECB (`sub_basic_dtl`, `crr_enqsubj_indv`, `subj_link`, `res_hdr_trail`, `req_indv`,
12  `req_comp`, `indv_basic_dtl`, `cntrct_smry`, ...) and `raw_account_master`, `raw_general_acct_mast_table`,
13  `general_acct_mast_table`.
14  Persisted copies are older than raw: salary stg loads to 2026-07-13 (raw 2026-10-13), bridge 2026-09-21, alert stg
15  2026-08-27 (raw 2026-10-14).
16
17  ## Bureau link (H1-H5)
18  - H1: **Confirmed: `subj_cntrct_link` is the bottleneck** 1,273,534 rows, 158,424 files, 103,759 subjects; 74,081 of
19    its files are in salary history = 2.93% of 2,530,796 files. Of 17,495 alert subjects of base CIFs, 147 are in it (152
20    CIFs). Lowercasing keys changes nothing (50,580 matches both ways). Its rows are mostly co-parties: role G 528,934, A
21    444,587, C 300,013
22  - H2: **`PRVDR_SUBJ_NUM` is the CIF** 3,346,281 of 3,589,864 values are 8 digits (same shape as base `cif_id`); 241,408
23    (10 chars, leading `_`) are dropped by `^\d+$`. Any transformation matches 17,623 base CIFs (94.1%); the rest have no
24    alert subject. Master `cif_no` is `UAE/EIB/EGY/KSA...` + 8 digits, so only the trailing digits match it (2,701,308 of
25    3.35M)
26  - H3: **No better link testable now** Existing tables only; subject / header / EID tables NOT AVAILABLE. Salary files
27    by table: con_tot_smry 100%, crdt_score 99.97%, cntrct_dtl 95.57%, cntrct_hist 88.9%, pymnt_order 10.0%, contract_link
28    2.93%, court_case 1.01%, bridge 0.01%
29  - H4: **Same id space; one report per pull** Exact and lowercased file ids match identically (74,081). One load date
30    per file-month; every file carries 36 months, so a CIF-month has several files (median 2; 3,179 of 5,283 have 2+, max
31    19). Pull date: NOT AVAILABLE (`res_hdr_trail`)
32  - H5: **No valid recommended link yet** See below
33
34  Base CIFs reached / with a salary month in 24 months (union, unresolved): today's bridge 109 / 39; contract_link + all
35  alert pairs (C1) 152 / 53; contract hop via `cntrct_dtl` (C7a) 152 / 88; via `cntrct_hist` (C7b) 72 / 43; provider app
36  no vs account id (C6) 19 / `<10`. Best union: 173 CIFs, 94 with a salary month (0.50% of base).
37  **Why none is usable:** a file lists every party of its contracts. Files with 2+ CIFs: C1 39% of 109,923 (198 of 383
38  touching base), C7a 69% of 130,164 (585 of 671). Today's bridge shows 1 CIF per file only because `dropDuplicates` keeps
39  one arbitrary subject per file, so even its 109 CIFs / 39 salary CIFs may be a co-party's salary. Defect, not fixed
40  (R19). Vote resolution leaves 234-300 files tied and 37-52 CIFs with a salary month, but the routes share one source, so
41  agreement (96-100%) is not independent evidence.
42  **What would fix it:** `sub_basic_dtl` (one subject `res_cb_subj_id` per file, 4.26M files in the profile) or
43  `crr_enqsubj_indv`. Restore these first, then rerun H3-H5. Stop-gap idea, untested: keep only the applicant role in
44  `contract_link`.
45
46  ## Bureau salary by another route (H3, `bo_rr_aecb_metric`)
47  Carries our `cust_num` next to each pull (no file bridge, as in RL). Base CIFs matched 3,831 (20.46%); 3,187 with last
48  salary credit > 0; 2,222 (11.9%) with that and a pull in 24 months. By `acct_num` 0 (loan vs card account formats).
49  Earliest pull per CIF 2020-09-09, p50 2024-05-15. Only customers who applied for a loan.
50
51  ## CASA part (C1-C3)
52  - C1: **WM flow, salary, labelled tables cover PRB/PSB/PB only; balance table behaves the same** Segment codes with 10+
53    CIFs: LIV., PSB, PRB, BB. PRB/PSB/PB 17,832 CIFs (95.2%) all have flow and salary rows (zero-filled spine); other
54    segments 834 and unknown 58 have none. Comp CASA txn in 12m: 12,231; 518 have no WM row (497 other, 21 unknown).
55    Balance row 11,849, but `<10` of the 834 other-segment CIFs, though code shows no segment filter on it (config differs
56    from what ran). The 197-CIF window waterfall is NOT VALID (null bug, fixed in code, not rerun)
57  - C2: **Not answerable: no dated account master loads** Bridge: 13,492 CIFs with an active account of any product (no
58    scheme, no dates), 12,880 seen in comp. Dormant: NOT IN JSON
59  - C3: **Depth is short; quote it per source** See below
60
61  C3 earliest month per CIF (min / p50): WM flow and salary table 2024-09 for all CIFs; first recoverable internal salary
62  2024-08 / 2024-09; WM labelled CASA txns 2021-01 / 2023-08; WM balance 2022-01 / 2023-05; comp 2023-01 / 2023-08; bureau
63  salary history loads from 2023-06-23 (salary months from 2020-07). Customer record start: 1962-07 / 2023-08-28 (18,666
64  have one). Record younger than source start: salary table 36.2%, comp 62.2%, labelled txns 84.2%, bureau load 52.7%.
65  No salary month in the WM salary table: 9,832 CIFs (52.5%); 3,810 joined after 2024-09 (their whole record is covered),
66  5,964 joined earlier (only 2024-09 onward observed), 58 no record date. Among 12,993 CIFs with CASA evidence (balance
67  row or comp txn in 12m): 4,101 have none (916 / 3,127 / 58).
68
69  ## Answers
70  - **Source defining "has a CASA with us":** a dated account master (`ecl.account_master` or `general_acct_mast_table`,
71    proposal in README) once it is in the catalog; open, closed, dormant cannot be counted before. Until then, balance row
72    or comp txn in 12m: 12,993 CIFs (69.4%); 5,731 (30.6%) have neither (upper bound for "no CASA with us"), and 558 CIFs
73    outside PRB/PSB/PB transact in comp yet have no WM flow row (A1 would call them Unknown).
74  - **Does WM cover the base?** Flow and salary: 95.2% (PRB/PSB/PB only). Balance: not for other segments, in the data.
75  - **"Ever" depth:** internal salary since 2024-09 (24 months), CASA transactions since 2023-01 (comp) or 2021-01
76    (labelled, segment-limited), bureau salary since the 2023-06 pulls. Quote "no salary in 24 months", not "never".
77
````

## Notes on specific spots
- Line 3: this file says 18,724 CIFs for `cc_60_180`. Other handoffs give 18,731 (3, 7, 12, 13, 20) and 18,725 (19). Copied as shown here; the three different values are worth a check in the source files.
- Line 18: "74,081 of its files are in salary history = 2.93% of 2,530,796 files" (74,081 / 2,530,796 = 2.93%, consistent). Line 29 repeats 74,081.
- Line 22: the quoted pattern is `^\d+$` as printed.
- Line 24: `UAE/EIB/EGY/KSA...` is as printed.
- Line 36: "`<10`" is a masked small count, as stated in line 5.
- Line 52-53: the segment group is written "PRB/PSB/PB" in most places; the heading of C1 reads "PRB/PSB/PB only". The segment codes with 10+ CIFs are listed as LIV., PSB, PRB, BB.
- Line 72-73 sums: 12,993 + 5,731 = 18,724, consistent with line 3's CIF count.
- Line 66-67: 12,993 CIFs with CASA evidence; "(916 / 3,127 / 58)" appears to split the 4,101 with no salary (916+3,127+58 = 4,101).
- Terminal and taskbar are not in these photos.
