# Handoff 25: `tmp_validation/a1_payment_cure/summary.md` (3 photos), 2026-11-02

## Context for Claude Code
- Source: 3 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest), taken 2026-11-02 ~13:57 Dubai. Tabs: `pipeline_registry.py`, `features.py`, `summary.md` (M = modified, active). Path: `tmp_validation > a1_payment_cure > summary.md`. Branch `feature/persona_redesign_b01*+`. Blame header: "You, 2 minutes ago | 1 author (You)"; line 1 blame: "You, 23 seconds ago - Uncommitted changes".
- Title: "A1 payment / cure validation - summary (CC `cc_60_180` | RL `rl_60_180`)". Validates the new A1 ability states (with the AECB/alert-salary route of handoffs 19, 23, 24) against 3-month payment, roll and cure outcomes, hypotheses H1-H7 and an answer. Follows handoffs 1-24.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and the run JSON.
- Photos overlap and are merged into source lines 1-75. Photo-to-line map (in the order sent): P1 = 51-75 (plus 1); P2 = 33-67 (plus 1); P3 = 1-35. Lines 33-35 and 51-67 appear in two photos each and agree.
- Table rows (lines 12-60) are markdown table rows where one source line is one table row, soft-wrapped in the editor; each is kept on one line here (shown wrapped at ~110 characters for readability only where marked). Notation in the file: `\|` is an escaped pipe separating "CC | RL" values inside table cells. `pp` = percentage points; intervals are 95% CIs in brackets.
- The whole file sits under a git diff gutter (blue bars = modified lines).

---

## `summary.md` (lines 1-75)

````
1   # A1 payment / cure validation - summary (CC `cc_60_180` | RL `rl_60_180`)
2
3   **Outcome source:** DPD = `crx_<p>_dpd_sequences` (month grain, canonical bucket); payments = CC
4   `raw_transaction` (via `build_cc_transactions`), RL `int_loan_master.payment_amount_mtd`; amount due
5   = A1 `liquidity_anchor_amt`; charge-off = bucket 180+. A1 from `crx_<p>_a1_ability` (has the step-8
6   columns). **Cohort months:** Jan-May 2026 (outcomes complete to Aug 2026, payments to Aug). Rows /
7   accounts / CIFs: CC 74,256 / 29,629 / 28,606; RL 12,512 / 5,416 / 4,957. Checks held: `agree_*` =
8   1.0; recomputed state = A1 state without AECB 99.98% (CC) / 100% (RL). All numbers are 3-month
9   outcomes, DPD-band-standardised differences in percentage points (pp) with 95% interval, pooled
10  rows; the latest-month-per-account view is cited where it differs. Association, not cause.
11
12  | Hyp | Verdict | Key numbers (CC \| RL) |
13  |---|---|---|
14  | H1 state order | **CONFIRMED** (CC: 10 of 12 outcomes; RL: Moderate > Low > Unknown on all 12,
15  High suppressed) | cure_3 high/mod/low/unknown CC 33.6/16.3/12.1/7.9%; roll_3 51.7/72.4/80.4/87.5%;
16  pay_any_3 53.5/42.2/32.5/19.1% (High = 161 accounts). RL mod/low/unk: cure 14.9/10.8/8.2; roll
17  70.3/80.3/86.3; pay_any 63.1/47.8/34.4. Exception: CC charge-off (mod 43.9% > low 42.2%); same in
18  the latest-month view |
19  | H2 would-be-Unknown | **CONFIRMED** | Stable vs none: cure_3 +4.8 [3.8, 5.7] \| +3.1 [-0.2, 6.3];
20  roll_3 -10.7 [-12.0, -9.4] \| -14.0 [-18.8, -9.2]; pay_any_3 +17.7 [16.2, 19.2] \| +23.5 [18.3,
21  28.7]; pay_due_3 +16.6 \| +20.4. Weak vs none: cure +2.1 \| +0.3 [-2.8, 3.4]; roll -5.9 \| -5.4;
22  pay_any +11.3 \| +12.1. Base (none): cure 7.9 \| 8.2%, roll 87.5 \| 86.3%, pay_any 19.1 \| 34.4%.
23  Rows: Stable 10,107 \| 723, Weak 5,293 \| 481, none 39,034 \| 5,182. Every cohort month same sign
24  (CC Stable pay_any +18.8 to +21.9 raw) |
25  | H2 would-be-Low | **CONFIRMED for Stable, UNCLEAR for Weak** | Stable vs none: cure_3 +2.8 [1.1,
26  4.5] \| +3.9 [0.5, 7.3]; roll -7.4 \| -11.4; pay_any +14.2 \| +24.1. Weak vs none: cure -1.1 [-2.9,
27  0.7] \| -1.2 [-4.3, 1.9]; roll -2.1 [-4.5, 0.3] \| -1.8 [-6.4, 2.8]; only pay_any +7.0 \| +12.8.
28  Weak mostly keeps its internal-salary state (CC 1,659 of 1,712 stay Low) |
29  | H3 AECB vs internal Stable | **REJECTED** (AECB Stable is not as good) | CC Stable: internal 591
30  accounts cure_3 33.0%, pay_any 61.0% vs bureau 6,893 accounts 14.4%, 40.7%; bureau - internal cure
31  -17.3 [-20.7, -13.8], roll +21.8, pay_any -19.4. Weak also worse: cure -10.0, pay_any -6.9. RL (57
32  internal accounts): cure -16.6 [-33.6, 0.4], roll +6.0 [-11.8, 23.7], pay_any +5.7 [-10.6, 21.9],
33  all intervals include 0 |
34  | H4 controls | **CONFIRMED for the Unknown population; weaker for Low** | Pooled rows. Unknown pop,
35  Stable vs none: cure, roll and pay_any keep their sign in every DPD band, amount-due tercile and
36  CASA-held split (CC); RL roll and pay_any hold everywhere, cure only for Personal Cash and CASA
37  held. Weak (CC): cure drops out at 91-120 (pooled) and 61-90, 91-120 (latest). Low pop (CC) Stable:
38  pay_any holds in every stratum, cure only at 61-90, lowest tercile and CASA held, roll at 61-90,
39  91-120 and all terciles, none at 121-180 for cure/roll; Weak only partly (pay_any, roll at 61-90).
40  The latest-month view loses more strata (e.g. pay_any at 121-180, top tercile) because of fewer rows
41  |
42  | H5 stopped salary | **CONFIRMED** worse; AECB salary **outlasts** the stop | Stopped vs not
43  (Stable): cure_3 -10.1 [-12.0, -8.2] \| -9.1 [-13.8, -4.5]; roll +15.8 \| +18.3; pay_any -15.0 \|
44  -19.2. Weak: -5.7/+11.0/-7.6 \| -4.3/+10.7/-9.3; none: -7.9/+12.5/-14.3 \| -7.6/+14.2/-24.5. Stopped
45  with AECB vs stopped without: pay_any +15.9 [12.9, 18.9] \| +23.1 [17.1, 29.1], roll -6.8 \| -6.5,
46  cure +3.2 \| +1.7 (ns). Alert path (4,647 \| 1,619 CIFs): positive alert share k=-3..0 1.4-1.8% \|
47  1.2-1.9%, then 5.0% (k+1), 12.1% (k+2), 9.0% (k+6) \| 4.0, 8.0, 6.7%; of 203 \| 55 CIFs with a
48  positive alert before, 59% \| 55% have one in k+1..6, 37% \| 35% in k+4..6, 56% \| 60% a closure
49  alert, 57% \| 53% a lower amount. Positive alerts do not die away |
50  | H6 25% check | **CONFIRMED: behave like Stable** | CC 25%-weak group (3,752 rows) vs Stable: cure
51  -0.6 [-2.0, 0.7], roll +2.8 [1.1, 4.5], pay_any -4.1 [-6.0, -2.1]; vs other Weak: cure +5.7, roll
52  -5.7, pay_any +6.4. Sparse months (2,793 rows) = Stable-like (pay_any -1.8 ns); real level falls
53  (774 rows) = Weak-like (vs Stable cure -5.5, roll +8.3, pay_any -11.8). RL (402 rows): vs Stable all
54  ns (roll +5.5 [-0.1, 11.0]); vs Weak cure +4.7, roll -7.7, pay_any +9.1; real falls 83 rows, sparse
55  301 |
56  | H7 data | **CONFIRMED: August is short, persisted alerts are stale** | Persisted alerts and
57  staging stop at 2026-08-27 (26 extract days); raw runs to 2026-11-01 (+66 days), Aug has 29 days to
58  08-30. Positive salary rows Aug vs Jul: CC 8,755 vs 15,443 (base CIFs 3,608 vs 5,640), RL 1,798 vs
59  3,663 (429 vs 702). A1 rows with a bureau salary May->Aug: CC 27.1->23.3%, RL 17.8->14.0%. Dormant rows
60  with only ambiguous legs in W, Aug: CC 352 of 6,744 (5.2%), RL 237 of 1,779 (13.3%) |
61
62  ## Answer
63  Yes. With DPD band controlled, an AECB salary separates better from worse payers, and the customers
64  it moved out of Unknown behave like the state they landed in. Among rows that would be Unknown, AECB
65  Stable pays any amount within 3 months 17.7 pp (CC) / 23.5 pp (RL) more than no-AECB rows, rolls
66  10.7 / 14.0 pp less, and cures 4.8 pp more (RL +3.1, not significant); AECB Weak gives about half of
67  that (pay +11.3 / +12.1) and no significant cure gain in RL. Controlling DPD band roughly halves the
68  raw charge-off gap (CC Stable -19.0 to -8.9 pp) and cure gap (+6.3 to +4.8); payment and roll gaps
69  barely move. Moved Stable rows cure 14.2% and pay 39.3% (Moderate overall 16.3%, 42.2%), but 10,107
70  of CC's 13,642 Moderate rows are these customers. Limits for GRR: AECB Stable is far weaker than
71  internal Stable (cure_3 -17 pp), the signal is mainly payment and roll, not cure, and the effect
72  shrinks in Low rows and at 121-180 DPD. August's bureau salary is under-counted until the alert
73  tables are refreshed. RL "High" is suppressed (under 10 accounts).
74
75
````

## Notes on specific spots
- The soft-wraps in the code block follow the editor line breaks seen in the photos, not hard line breaks in the file. Source line numbers are the editor's (gutter numbers 1-75).
- `\|` inside the table cells is how the file writes a pipe within a cell (CC value `\|` RL value).
- Line 14: "10 of 12 outcomes" and the "High suppressed" note are read as printed. Line 17: "(mod 43.9% > low 42.2%)" is a charge-off exception where Moderate is worse than Low.
- Line 22: base (none) values: cure 7.9 | 8.2%, roll 87.5 | 86.3%, pay_any 19.1 | 34.4%. They match the line 15-17 unknown values (7.9, 87.5, 19.1 CC; 8.2, 86.3, 34.4 RL).
- Line 69: "Moved Stable rows cure 14.2% and pay 39.3% (Moderate overall 16.3%, 42.2%)" is read as printed; 16.3% and 42.2% also appear as the CC moderate cure_3 and pay_any_3 in line 15-16.
- Line 59: the arrows are written `->` (a right arrow in the photo, "27.1>23.3%").
- Lines 33 and 41: line 33 is the end of the H3 row (`all intervals include 0 |`); line 41 is a lone `|` ending the H4 row. Both are real source lines in the photos.
- Terminal and taskbar are not in these photos. The photos show "Sodium Free" packaging and the window behind the laptop; nothing to transcribe from it.
