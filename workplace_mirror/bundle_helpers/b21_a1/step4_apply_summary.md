# Handoff 57: `data/input/a1_bundle21_apply_summary.md` lines 1-107 (A1 bundle 21 - apply summary: cross-product, WM labels, flow classes, check outcomes, tests) (2 photos), 2026-11-10

## Context for Claude Code
- Source: 2 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest`, workspace `retail.collections.risk_profiling`; menu bar shows "Help"). Tabs: `pipeline_registry.py` (M = modified), `21_a1_evidence_family_rule.md`, `a1_bundle21_apply_summary.md` (active, saved, no U or M mark). Breadcrumb `data > input > a1_bundle21_apply_summary.md > # A1 bundle 21 - apply summary (cross-product, WM labels, flow classes, check outcomes, tests)`; the start of the path is cut off at the left edge, so the folder above `data` is not visible (the file is under `data/input/`).
- Content: the apply summary for A1 bundle 21 (the implementation of the round-3 findings of handoffs 50 and 55, from `21_a1_evidence_family_rule.md`): the cross-product feature (F4), WM labels join, class table against the flow dictionary, outcomes in the check (`cohort_outcome_lines`, `compare_a1`), and catalog / tests / registry. Written by a Claude Code session ("the apply"). Follows handoffs 1-56.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photos overlap and are merged into source lines 1-107. Photo-to-line map (in the order sent): photo 1 = lines 1, 40, 54-107; photo 2 = lines 1-59. Line 107 is the last line shown (blank); I cannot tell whether the file continues.
- Source lines are hard-numbered in the editor. Paragraphs and bullets are one source line each, wrapped by the editor; the wrapped visual lines keep the number of their start line only where the editor shows a number (as numbered below).
- Written in the cloud workspace; saved to `~/Python/Collections/pics/claude_code_handoff_57.md` through the Mac link if it is up (see the chat reply); otherwise copy it there.

---

## `a1_bundle21_apply_summary.md` (lines 1-107)

````
1   # A1 bundle 21 - apply summary (cross-product, WM labels, flow classes, check outcomes, tests)
2
3   All five items are in, and 94 tests pass across the new test files and the existing CASA test. Nothing ran against PROD
4   data and `kedro run` was not used. `kedro registry list` shows `product_features`, `crx_cc_a1_check` and
5   `crx_rl_a1_check`, and every dataset those pipelines read exists in the catalog. Black and pylint are clean on the files
6   touched.
7
8   ## 1. Cross-product feature
9
10  `feat_cif_cross_product.build` follows the snippet's F4 sources, with the exact `COLUMNS`. Cards are contracts, so
11  supplementary cards never appear, and a card that a newer card replaced is dropped. CASA balances are not read.
12
13  - **The stub's dataset names were wrong, so the signature widened.** `wm_fea_aum_balance` does not exist in the
14    catalog. `prm_balance` only holds the model's own delinquent contracts, so it cannot supply other cards. The snippet
15    got deposits and investments from `wm_fea_casa_eod_avg_balance`, AUM from `wm_fea_wealth_holdings_by_cif`, and cards
16    from five raw Way4 tables.
17  - `build` now takes `wm_balances`, `wm_holdings` and five `card_*` frames. `product_holding` and `loan_portfolio` are
18    unchanged. `pipelines/products/features.py` is wired to those names.
19  - **Asset rows have no real account id.** The WM sources are per customer, so deposit, investment and WM rows carry the
20    fixed ids `ITD`, `INV` and `WM_AUM`.
21  - **Other design points:**
22    - Balances of zero or less are dropped.
23    - A term-deposit holder with no balance snapshot gets a `deposit` row with a NULL balance.
24    - The node covers all customers, bounded by date, like its CASA siblings.
25
26  **Two differences from round 3:**
27
28  - Round 3 reported AUM but never scored it. `build_cross_product_signals` sums `wm` into `xp_assets_aed`, so F4 will
29    now count it.
30  - Round 3 treated "term-deposit count above 0" as `some`. The engine's `xp_holding` needs a balance above 0, so the
31    NULL-balance rows do not count.
32
33  ## 2. WM labels
34
35  `WM_SELF_COLUMN` is `self_transfer_flag` and `WM_SELF_VALUE` is 1. Both tables carry `tran_id`: the committed round-3
36  results show the join key was used and `summary_r3.md` reports a 94.2% match. Round 3 also joined on direction
37  (`in_out_flow`), so the node does too. Without it, a self label on one leg of a shared `tran_id` could bleed onto the
38  opposite leg.
39
40  ## 3. Class table against the dictionary
41
42  The real `flow_class()` was run over every combination in both dictionaries. The comparison script is in
43  `/tmp/flowcmp`, outside the repo.
44
45  **Changed.** The dictionary is explicit on two WM labels the bundle had no rule for:
46
47  - A debit with a `fees_charges` label is now `bank_initiated`. It sits after the `card_payment` and `own_loan` lanes
48    and does not apply to salary-flagged legs. This moves about AED 37M in CC and 8M in RL out of money out.
49  - A debit with a `loan_payment_flag` and no bank counterparty is now `unplaced`, since the instalment may be our own
50    loan. This is about AED 4M in CC and 1M in RL.
51
52  Both need extra WM flag columns in the labels join. The three user decisions are untouched (cash deposits count,
53  own-account transfers with other banks count both ways, `MISCELLANEOUS` / cheque stems never count).
54
55  **Still differing (23 CC and 13 RL combinations, none changed).** The bundle has its own rule in each case. AED is
56  the sum of the differing combinations.
57
58  | Dictionary -> bundle | CC AED | RL AED | Why left alone |
59  |---|---|---|---|
60  | `third_party_in` -> `salary` (WM salary-flagged credits) | ~340M | ~164M | Salary is its own class by design |
61  | `own_transfer` -> `salary` (subsidiary credit, 506 salary) | 2.4M | - | Bundle checks salary before lane |
62  | `own_transfer` -> `own_in/out_external` (wash lane, self) | 9.6M, 5.3M, 4.0M | 2.4M, 1.2M, 1.0M | Self before lane |
63  | `unplaced` -> `third_party_in` (mirrored credits, mirror gate) | 2.9M | 0.7M | Handled by runtime netting |
64  | `debt_elsewhere` -> `chosen_spend` | 1.1M | 0.3M | Both count as spend; no such class |
65  | `reversal_return` -> `chosen_spend` (bank debits near DDS event) | 0.2M | 0.2M | Needs event data not in bundle |
66  | `bank_initiated` -> `own_out_external` (charges lane, self+fee) | ~0 | - | Same self-before-lane order |
67
68  Notes on the table:
69
70  - The wash-lane self-label rows are DDR return and DDS legs that are 100% mirrored; netting should drop most of them.
71    They are the ones to look at, because the bundle's order disagrees with the dictionary's lane-first order.
72  - The salary row is the largest in AED, but it is the bundle's design.
73
74  ## 4. Outcomes in the check
75
76  `cohort_outcome_lines` ports the round-3 definitions: the Jan-May 2026 cohort, 61-180 DPD at observation, and `cure_3`,
77  `pay_any_3` and `roll_3`. It reports raw rates with 95% CIs clustered on the CIF, n per state, and High-Moderate and
78  Moderate-Low gaps standardised to the better state's DPD-band mix. Cells under 10 accounts show `<10`, and no ids are
79  logged.
80
81  `compare_a1` gained four inputs: `crx_<p>_obs_base`, `crx_<p>_dpd_sequences`, and `raw_transaction` (CC) or
82  `int_loan_master` (RL). The two sequence datasets must exist for 180+ model_ids too, even though outcomes are not
83  computed there.
84
85  ## 5. Catalog, tests, registry
86
87  - **Catalog:** the only keys removed from `catalog_crx.yml` and `catalog_casa.yml` relative to HEAD are the two
88    `crx_<p>_a1_liquidity_signals`. The eight keys listed in the brief each exist exactly once. Nothing needed putting
89    back.
90  - **Registry:** the apply had also dropped the four `casa_windows*` imports and registry entries. Their modules and
91    catalog entries still exist and `TASKS.md` E4 still refers to them. They were restored as in HEAD, so the registry
92    diff is now additive only.
93  - **Tests:** the repo had no A1 tests and no liquidity tests, and `workplace_mirror` is not in this workspace, so the
94    92 cases could not be aligned to. New tests were written instead:
95    - `test_a1_ability.py` covers the four levels, the CASA and cross-product builders, the scorecard, the check's
96      outcome helpers and an RL cohort end to end.
97    - `test_feat_cif_cross_product.py` covers the cross-product node.
98    - `test_feat_cif_casa_flows.py` covers every class and `build_casa_flows`.
99
100 **Mishap, fixed.** The first black run reformatted 13 unrelated files in `nodes/features`. None had prior changes, so
101 they were restored from HEAD; `git status` shows only the intended set.
102
103 ## Open questions
104
105 - Should the bundle put the lane ahead of the self label for wash-lane legs, as the dictionary does?
106 - Should AUM stay in `xp_assets_aed`, given round 3 never scored it?
107
````

## Notes on specific spots
- No sum checks apply (almost no tables). The one cross-reference: line 36 says `summary_r3.md` reports a 94.2% match, which matches handoff 55 line 42 (94.2% of CC flagged salary keys find a leg; RL was 96.7%). The AED figures in lines 48 and 50 (about 37M CC / 8M RL; 4M CC / 1M RL) have no counterpart in earlier handoffs.
- Line 3 says 94 tests pass; line 94 says the "92 cases could not be aligned to" (a different, earlier set of cases), as printed.
- Line 55: "23 CC and 13 RL combinations" differ, but the table lines 60-66 lists 7 classes (several rows hold more than one combination, e.g. line 62 with three CC values 9.6M, 5.3M, 4.0M and three RL values 2.4M, 1.2M, 1.0M). As printed.
- Lines 70-71: "DDR return and DDS legs" is as printed. Line 90: `casa_windows*` has a literal `*` (wildcard), as shown.
- Line 62: the AED cells list three values each (`9.6M, 5.3M, 4.0M` and `2.4M, 1.2M, 1.0M`), as printed.
- File name `21_a1_evidence_family_rule.md` is the second tab (not transcribed here); `pipeline_registry.py` has an M mark (modified), as shown in both photos.
- OCR-risk digits: AED figures on lines 48, 50, 60-66 (37M, 8M, 4M, 1M, ~340M, ~164M, 2.4M, 9.6M, 5.3M, 4.0M, 1.2M, 1.0M, 2.9M, 0.7M, 1.1M, 0.3M, 0.2M), counts on lines 3, 55, 94, 100 (94, 23, 13, 92, 13), and the 94.2% on line 36.
