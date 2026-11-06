# A3 V1d cascade addendum (cc_60_180), verbatim from handoff 46 (2026-11-06)

## `results_v1d_cc_60_180_CAS.md` (lines 1-63)

````
1   # A3 V1d results - cc_60_180
2
3   Snippet `a3_v1d_snippet.py`; see `README_v1d.md`. Groups G1 (DCORE paid, ledger not kept), G2 (paid, kept), G3 (overdue) over the V1c concluded instalments. Cells of 1-9 are `<10`.
4
5   ## Population and groups
6
7   - model `cc_60_180`; latest month 2026-08-31; run type full
8   - accounts in the population 19,292; agreements 19,277
9   - scalars used for the source filters: plan start min lo = 2024-08-03; max due date = 2026-08-30; hi = max(max due + 30 d, observation date) = 2026-09-29; outcome sources read to 2026-12-08 (max due + 100 d, two cycles after); EDP buffer 12 months
10  - groups: G1 = DCORE paid and ledger not kept at the cut-off (due date + 5 d); G2 = DCORE paid and ledger kept; G3 = DCORE overdue; ND = ledger no data (excluded)
11
12  | plan | instalments | G1 | G2 | G3 | ND |
13  |---|---|---|---|---|---|
14  | PTP | 4,701 | 207 (4.4%) | 460 (9.8%) | 4,034 (85.8%) | 0 (0.0%) |
15  | Settlement | 12,151 | 3,813 (31.4%) | 2,027 (16.7%) | 6,311 (51.9%) | 0 (0.0%) |
16
17  ## Cascade - first miss vs behind an earlier miss
18
19  Each instalment is checked against the instalments of the same plan that fall due earlier (only those in the analysed list: concluded, in the 12-month window, after the anchor). 'Behind an earlier miss' = an earlier instalment was not kept at its own cut-off. 'Pays its own amount alone' = cumulative paid at the cut-off >= this instalment's own due amount (a cascade-free reading).
20
21  ### G1 by position in the plan
22
23  | plan | group | instalments | G1 is=behind an earlier miss | G1 is=first / no earlier miss |
24  |---|---|---|---|---|
25  | PTP | G1 paid, ledger not kept | 207 | 0 (0.0%) | 207 (100.0%) |
26  | Settlement | G1 paid, ledger not kept | 3,813 | 2,471 (64.8%) | 1,342 (35.2%) |
27
28  ### Cascade-free reading: does the money paid by the cut-off cover this instalment's own amount?
29
30  | plan | group | instalments | behind an earlier miss | pays own amount alone | behind a miss and pays own amount |
31  |---|---|---|---|---|---|
32  | PTP | G1 paid, ledger not kept | 207 | 0 (0.0%) | 0 (0.0%) | 0 () |
33  | PTP | G2 paid, ledger kept | 460 | 0 (0.0%) | 460 (100.0%) | 0 () |
34  | PTP | G3 overdue | 4,034 | 0 (0.0%) | 323 (8.0%) | 0 () |
35  | Settlement | G1 paid, ledger not kept | 3,813 | 2,471 (64.8%) | 2,731 (71.6%) | 2,325 (94.1%) |
36  | Settlement | G2 paid, ledger kept | 2,027 | 358 (17.7%) | 2,027 (100.0%) | 358 (100.0%) |
37  | Settlement | G3 overdue | 6,311 | 4,997 (79.2%) | 4,391 (69.6%) | 3,953 (79.1%) |
38
39  ### G1 instalments per plan (plan level)
40
41  | plan type | G1 instalments in the plan | plans | G1 instalments |
42  |---|---|---|---|
43  | PTP | 1 G1 instalment | 207 | 207 |
44  | Settlement | 1 G1 instalment | 561 | 561 |
45  | Settlement | 2-3 | 433 | 1,037 |
46  | Settlement | 4 or more | 348 | 2,215 |
47
48  ## Source filters and partitions read
49
50  | source | partition column | filter form | window | partitions seen |
51  |---|---|---|---|---|
52  | - | - | - | - |
53
54  PartitionFilters as printed by `explain()`:
55
56
57  ## Runtime
58
59  | part | time |
60  |---|---|
61  | setup | 1m24s |
62  | Cascade: first miss vs behind an earlier miss | 0m05s |
63  |
````

## Terminal excerpt (bottom panel, as shown; not part of the file)
````
[root@lvenaacaai402b retail.collections.risk_profiling]# hdfs dfs -rm -r hdfs://cdpprod/ai_data/sandpit_aacoe/ai_adv/enbd/risk_collect
ck …
crx/crx_rl_a1_ability_b14_check' to trash at: hdfs://cdpprod/ai_data/sandpit_aacoe/.Trash/balzsv/Current/ai_data/sandpit_aacoe/ai_adv/enbd/risk_c
ollections/dev/rl_60_180/10_persona/crx/crx_rl_a1_ability_b14_check
[root@lvenaacaai402b retail.collections.risk_profiling]# 
````
The terminal shows the end of an `hdfs dfs -rm -r` of the dev `rl_60_180` output `crx_rl_a1_ability_b14_check` (moved to the HDFS trash). The command text is wrapped and cut by the terminal ("risk_collect" then "ck …"), and the first line of the command output is also cut off, so the full source path is reconstructed from the trash path: `.../ai_adv/enbd/risk_collections/dev/rl_60_180/10_persona/crx/crx_rl_a1_ability_b14_check`.

## Notes on specific spots
- Sum checks that pass: 207 + 460 + 4,034 = 4,701 and 3,813 + 2,027 + 6,311 = 12,151 (lines 14-15), with the shares as printed (207 / 4,701 = 4.4%, 3,813 / 12,151 = 31.4%); 2,471 + 1,342 = 3,813 and 64.8% + 35.2% = 100% (line 26); 561 + 433 + 348 = 1,342 = the "first / no earlier miss" count on line 26, and 561 + 1,037 + 2,215 = 3,813 (lines 44-46); 2,325 / 2,471 = 94.1% (line 35) and 3,953 / 4,997 = 79.1% (line 37); 323 / 4,034 = 8.0% (line 34).
- Lines 32-34: the last column shows `0 ()` with empty parentheses (no percentage because the denominator is 0), as printed.
- Line 23: the column header reads "G1 is=behind an earlier miss" and "G1 is=first / no earlier miss", as printed (the `=` is in the source).
- Line 52: the table body is a row of `-` cells with four cells under a five-column header, and line 54 ("PartitionFilters as printed by `explain()`:") is followed by blank lines 55-56, i.e. nothing was printed. The "Source filters and partitions read" section is empty in this file, as shown.
- Line 63 is a lone `|`, the start of a new runtime row (cursor line). The runtime table has only two rows (setup 1m24s; Cascade 0m05s).
- Line 9: the scalar dates (2024-08-03, 2026-08-30, 2026-09-29, 2026-12-08) and "12 months" are OCR-risk digits. 2026-12-08 is later than the run month (2026-08-31), as printed ("max due + 100 d, two cycles after").
- OCR-risk digits: lines 8, 14-15, 25-26, 32-37, 43-46 (counts and percentages), and the times on lines 61-62.
