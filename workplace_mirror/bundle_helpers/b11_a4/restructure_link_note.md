# Handoff 26: `tmp_validation/rl_restructure_link/README.md` (3 photos), 2026-11-02

## Context for Claude Code
- Source: 3 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-11-02 ~13:59 Dubai. Tabs: `pipeline_registry.py`, `features.py`, `README.md` (U = untracked, active, italic = preview/untracked). Path: `tmp_validation > rl_restructure_link > README.md`. Branch `feature/persona_redesign_b01*+`.
- Title: "RL restructure -> original-loan link: know-how for the A4 deterioration rework". A hand-over note: how the restructured-to-original loan link is built (`int_loan_restructure_link.py`), the resulting columns, where the A4 persona deterioration logic loses history today, a suggested design (proposal, not agreed), pitfalls and working rules. Follows handoffs 1-25; it is a spec for a new task, not a results file.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify code identifiers (backticked names, file paths) against the repo.
- Photos overlap and are merged into source lines 1-84. Photo-to-line map (in the order sent): P1 = 1, 52-84; P2 = 1, 25-60; P3 = 1-36. Lines 25-36 appear in P2 and P3, lines 52-60 in P1 and P2; they agree.
- The file is Markdown; soft-wrapped lines in the editor are single source lines unless a gutter number shows otherwise. Line numbers below are the editor's gutter numbers; continuation lines (soft-wrap) are shown indented without a number.

---

## `README.md` (lines 1-84)

````
1   # RL restructure -> original-loan link: know-how for the A4 deterioration rework
2
3   Goal: make the retail-loan (RL) deterioration logic (persona axis A4, `pipelines/crx_persona/_dpd_journey` +
4   `rl_a4_deterioration`) see a restructured loan's **full history** by stitching in the closed predecessor loan(s).
5   Today a restructure closes the old account and opens a new one, so the new account looks like a fresh contract.
6   Self-contained: everything needed is in the code paths named below. No data access; verify by reading and unit tests.
7
8
9   ## 1. How the link is built (`nodes/intermediate/retail_loans/int_loan_restructure_link.py`)
10  No source column names the predecessor (`ra_prev_ln_acct_num` is migration lineage, not restructuring), so it is
11  inferred from `int_loan_master`. Output `int_loan_restructure_link`: one row per (restructured acct x predecessor).
12
13  | Rule | Detail |
14  |---|---|
15  | Restructured R | first month `is_restructured = 1`; keeps `restr_flagged_date`, `restr_disbursement_date` |
16  | Closed C | first month `account_status = 'CLOSED'`; `orig_close_date = loan_status_date` |
17  | Edge | same `cif_id`, same product bucket, `abs(R.disbursement - C.close) <= 7` days, different account |
18  | Product buckets | Personal = Personal Cash; Auto and Fleet kept apart; Home; Other. Cross-family never matches |
19  | Assignment | mutual-best 1:1 (days apart, amount gap, ids), then leftover closed loans join a matched new loan |
20  | `match_type` | `one_to_one` or `many_to_one` (consolidation); unmatched R has null `orig_*`, `candidate_count` = 0 |
21  | Predecessor attrs | `orig_last_outstanding` (last non-zero), `orig_peak_dpd`, `orig_dpd_pre_close` (pre-closure) |
22
23  The link is **inferred, not observed**: treat it as probable. `candidate_count > 1` means an ambiguous window.
24
25  ## 2. The columns (account grain, point-in-time at `observation_date`)
26  | Column | Module | Meaning |
27  |---|---|---|
28  | `has_restructured_loan_flag` | `feat_loan_restructure.py` | 1 if any snapshot <= obs has `is_restructured = 1` |
29  | `restructuring_count_12m` | same | distinct restructure dates (fallback: first flagged month) within 12m |
30  | `days_since_last_restructuring` | same | obs - latest `restructuring_date` (NULL if never restructured) |
31  | `restructured_loan_outstanding` | same | balance in the obs-date snapshot only (current, not historical) |
32  | `has_restructured_loan_active` | same | 1 if that balance > 0 |
33  | `orig_loan_matched_flag` | `feat_loan_restructure_origin.py` | 1 if R flagged AND predecessor closed, both <= obs |
34  | `orig_loan_acct_num` / `orig_loan_closed_dt` | same | latest-closed predecessor (id breaks same-day ties) |
35  | `orig_loan_outstanding_at_close` | same | SUM of last non-zero balances across predecessors |
36  | `orig_loan_peak_dpd` / `orig_loan_dpd_pre_close` | same | MAX over predecessors (worst, not latest) |
37  | `days_since_orig_close` | same | obs - most recent predecessor close |
38  CIF grain adds `restructured_loan_count`, `has_multiple_restructured_loans_flag`. Unmatched rows: flag 0, rest NULL.
39
40  ## 3. Where the persona deterioration logic loses the history today
41  | Step | File (`pipelines/crx_persona/`) | Behaviour |
42  |---|---|---|
43  | Scope | `rl_full_history/nodes.py` | `int_loan_master` leftsemi `rl_spine` ids: **predecessors dropped** |
44  | Rename | same | `is_restructured` -> `restructure_flag`; `dlq_bucket` = `dpd_bucket` (0 = 0 DPD ... 7 = 180+) |
45  | Sequence | `_dpd_journey/spark.py::build_dpd_sequences` | per-account bucket array; flag = MAX restructure flag |
46  | State | `_dpd_journey/states.py::assign_state` | `history_blind` = cropped or restructure_blind_spot` gates Q0/Q1/Q4 |
47  | Entry | `rl_a4_deterioration/nodes.py` | thin wrappers; engine adds +1 bucket offset (RL 1 = 1-30 DPD) |
48  Consequence: a restructured loan looks like a fresh contract, so a long-delinquent customer can be mislabelled
49  `early_payment_default`/`straight_roller`; the widened guard forces `unknown`/`seasoned` for the account's whole life
50  (the flag is static). Linking should replace that blanket blindness with real history where matched.
51
52  ## 4. Suggested design (proposal, not agreed - confirm with the user before building)
53  Additive only: new modules, new nodes, new `crx_rl_`-prefixed outputs, new catalog entries. Never edit existing nodes.
54  1. New node `crx_rl_full_history_linked`: scope = spine ids UNION predecessor ids taken from `int_loan_restructure_link`
55     (never scan `int_loan_master` unscoped: billion-row table). Drop predecessor `CLOSED` rows (zero DPD fakes a cure).
56  2. Re-key predecessor rows to the restructured account id; for `many_to_one` take the worst bucket per month. Where
57     months overlap (disbursement ~ close date, tolerance 7d) prefer the restructured loan's own row.
58  3. Run `build_dpd_sequences` on the stitched history; no engine change needed if `restructure_flag` is zeroed for
59     matched chains and kept at 1 for unmatched ones (they stay blind spots).
60  4. No leakage: use a predecessor only if `restr_flagged_date <= obs` and `orig_close_date <= obs`. The link is built
61     from the whole master, so un-gated use leaks the future. Use only data on or before the observation date.
62  5. Emit audit columns: `chain_stitched_flag`, `chain_n_predecessors`, `chain_match_type`, `chain_candidate_count`,
63     `chain_months_added`. Optionally feed `orig_loan_peak_dpd` / `orig_loan_dpd_pre_close` into the state tree.
64  6. Compare old vs new `crx_rl_a4_deterioration` state mix on the same population (side-by-side evidence).
65
66  ## 5. Pitfalls to check
67  - Chains: a restructured loan can itself later be a closed predecessor. Resolve transitively; guard against cycles.
68  - Bucket scheme: keep RL native 0-7 in the stitched array; do not mix with the +1-shifted CC scale.
69  - Cross-product restructures (Personal -> Auto) stay unlinked by design: report their share.
70  - `is_restructured` is sparse (~0.5%, a "terms rewritten this month" event flag); the user rejected it as a reliable
71    succession marker, and the link only covers accounts it flags, so recall is unknown.
72  - Loans have month-end snapshots only: no intra-month timing; predecessor and new loan may share a month.
73  - Never derive features from nationality, visa status, gender or close proxies. Results files: aggregates only.
74  - The existing flag is static per account, so a restructured account is "blind" for its whole life; decide whether
75    the stitched version should decay it.
76
77  ## 6. Working rules
78  - Never run `kedro run` (no PROD data here). Use `python -m py_compile`, unit tests, and a read-only PROD validation
79    snippet for the user to run (parametrise by `model_id`, aggregates only, absolute paths resolved from `__file__`).
80  - Tests to extend (new files, not edits): `src/tests/nodes/features/retail_loans/test_feat_loan_restructure_origin.py`,
81    `src/tests/nodes/intermediate/retail_loans/test_int_loan_restructure_link.py`, `src/tests/nodes/crx_persona/`
82    (`test_dpd_journey*.py`). Three `build_rl_full_history` `cif_id` fixture failures pre-exist; they are not yours.
83  - Before any commit: run `black`, then pylint. Do not commit or push unless asked. Do not touch `cc_dpl`.
84
````

## Notes on specific spots
- Line 46: the photo shows `history_blind` = cropped or restructure_blind_spot` with a missing opening backtick before `restructure_blind_spot` (a typo in the source as shown); kept as printed.
- Line 53: ends "Never edit existing nodes." and line 54 begins the numbered list; the numbered items 1-6 sit on lines 54-64 as in the photos (continuation lines 55, 57, 59, 61, 63 are the wrapped second lines of each item).
- Lines 3-6: the file refers to `pipelines/crx_persona/_dpd_journey` + `rl_a4_deterioration` as the A4 (deterioration) axis code paths.
- Line 38 is the last line of the section 2 table with the CIF-grain note (no blank line before it, as shown).
- Line 47: "engine adds +1 bucket offset (RL 1 = 1-30 DPD)" is the RL bucket scheme; line 44 gives the native scheme "0 = 0 DPD ... 7 = 180+".
- Line 20: "candidate_count = 0" for unmatched R is as printed.
- The photos also show the laptop and a Nestle "Sodium Free" label in the background; nothing to transcribe from that.
- Path in line 80-82 are OCR-risk (long test file names); verify against the repo tree.
