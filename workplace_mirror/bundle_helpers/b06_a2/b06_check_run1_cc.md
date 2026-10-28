# Bundle 06 check — first PROD run (cc_60_180, 2026-10-28)

`tmp_validation/a2_b06_run_log_summary.md` at work (handoff 15, 3 photos, OCR quality). Nodes 1–9 ran; node 10
(`compare_crx_cc_a2_b06`) failed because the PROD old output still has the single-state schema
(`a2_state_v1`), node 11 (RULES) never ran. Fixed in bundle 07; resume with the two nodes.

## `a2_b06_run_log_summary.md` (lines 1-83)

````
1   # A2 b06 check run: log summary (2026-10-28, model_id=cc_60_180)
2
3   Run result: 9 of 11 nodes completed. Node 10 (`compare_crx_cc_a2_b06`) failed.
4   Node 11 (`describe_crx_cc_a2_b06_rules`) never ran.
5   Resume with: `--from-nodes "compare_crx_cc_a2_b06,describe_crx_cc_a2_b06_rules"`
6
7   ## Node timeline (start 12:08, Spark env: medium)
8   - build_crx_cc_obs_base: about 17 s
9   - build_prm_dcore_account_agreements: about 9 s
10  - build_crx_cc_a2_dcore_signals: about 31 s
11  - build_crx_cc_a2_demographics_deceased: about 6 s
12  - build_crx_cc_a2_way4_deceased: about 10 s
13  - build_feat_cif_location_monthly: about 12.5 min (slowest, 12:10 to 12:23)
14  - describe_crx_cc_a2_b06_debit: about 1.6 min
15  - build_crx_cc_a2_location_signals: about 8 s
16  - build_crx_cc_a2_locatability: about 3 s
17
18  ## B06 DEBIT: August month rows (month x type x place, count, share of all rows)
19  ```
20  2023-08-01 x ATM     x abroad    576  0.0%
21  2023-08-01 x ATM     x uae     12694  0.2%
22  2023-08-01 x Offline x abroad   6273  0.1%
23  2023-08-01 x Offline x none      271  0.0%
24  2023-08-01 x Offline x uae     89772  1.7%
25  2023-08-01 x Online  x abroad    230  0.0%
26  2023-08-01 x Online  x uae       319  0.0%
27  2024-08-01 x ATM     x abroad    716  0.0%
28  2024-08-01 x ATM     x uae     12854  0.2%
29  2024-08-01 x Offline x abroad   8796  0.2%
30  2024-08-01 x Offline x none      234  0.0%
31  2024-08-01 x Offline x uae    122025  2.3%
32  2024-08-01 x Online  x abroad    245  0.0%
33  2024-08-01 x Online  x uae       456  0.0%
34  2025-08-01 x ATM     x abroad    633  0.0%
35  2025-08-01 x ATM     x uae     12302  0.2%
36  2025-08-01 x Machine x abroad   7498  0.1%
37  2025-08-01 x Machine x uae    137724  2.6%
38  2025-08-01 x NULL    x none      101  0.0%
39  2025-08-01 x Online  x abroad    156  0.0%
40  2025-08-01 x Online  x uae       563  0.0%
41  2026-08-01 x ATM     x abroad     11  0.0%
42  2026-08-01 x ATM     x uae       325  0.0%
43  2026-08-01 x Machine x abroad    230  0.0%
44  2026-08-01 x Machine x uae      4545  0.1%
45  2026-08-01 x Online  x abroad      4  0.0%
46  2026-08-01 x Online  x uae        14  0.0%
47  ```
48  Other B06 DEBIT facts (all months, about 5.27M rows):
49  - Offline is replaced by Machine from 2025-01 on.
50  - 2026-05 to 2026-10 volumes fall to about 0.0-0.1% (partial-month or lagged data).
51  - place_source: merchant_country 90.4% (Machine 38.9%, Offline 51.1%, Online 0.4%), narration 9.4% (ATM), counter_part... [cut off at right edge]
    0.1%.
52  - reason_for_excluding: None 5,268,406 (100%), CHARGES 13.
53
54  ## Final state distribution (a2_state, month of 2026-08-31, n=19,292)
55  ```
56  deceased                       89   0.5%
57  in_country__non_reachable    2613  13.5%
58  in_country__reachable        1648   8.5%
59  in_country__unknown           369   1.9%
60  skip__non_reachable          6114  31.7%
61  skip__reachable              1186   6.1%
62  skip__unknown                1155   6.0%
63  unknown__non_reachable       4290  22.2%
64  unknown__reachable           1203   6.2%
65  unknown__unknown              625   3.2%
66  ```
67
68  ## Error and its source
69  `AnalysisException [UNRESOLVED_COLUMN.WITH_SUGGESTION]`: column `location_state` cannot be resolved.
70  - Failing node: `compare_a2_outputs()` in
71    `src/enbd_collections/pipelines/crx_persona/a2_locatability/b06_check.py:74`
72    (the `.select(...)` on the OLD frame).
73  - Cause: the OLD dataset (`crx_cc_a2_locatability`, read from PROD) still has the v1
74    schema: `a2_state_v1, a2_confidence, a2_provenance, rpc_rate, ptp_flag, computed_at, ...`.
75    The compare code expects `location_state`, `reachability_state` and `deceased_flag_v2`
76    (lines 76-78), which are not in that dataset.
77  - Not a data problem. The new engine output and the debit and rules logic are fine.
78    The old-vs-new comparison assumes the wrong old schema.
79  - Fix options:
80    - Derive old location, reachability and deceased from `a2_state_v1` and `deceased_flag`.
81    - Or point `old` at a version that has the v2 columns.
82    - Then rerun only the two remaining nodes (resume command above).
83
````

