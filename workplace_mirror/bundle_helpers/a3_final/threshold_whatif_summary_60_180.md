# Handoff 52: `tmp_validation/a3_thresholds/summary.md` lines 1-59 (A3 threshold what-if, 2026-11-09) (2 photos), 2026-11-09

## Context for Claude Code
- Source: 2 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest`, workspace `retail.collections.risk_profiling`, branch `feature/persona_refactor*`). Tabs: `pipeline_registry.py`, `17_a3_credibility_engine.md`, `summary_v1f.md`, `summary.md` (active). Path `tmp_validation > a3_thresholds > summary.md`, breadcrumb `# A3 threshold what-if — summary (2026-11-09)`. Blame "You, 1 hour ago | 1 author (You)"; status bar: "You, 1 hour ago", "vajdab (1 hour ago)", Ln 2, Col 1, Spaces: 2, UTF-8, LF.
- Content: a what-if on the A3 (payment credibility) point thresholds, on `crx_<p>_a3_check_payments`, latest month 2026-08-31, one row per account (CC `cc_60_180` n = 19,292; RL `rl_60_180` n = 3,985). Setting names: `M` = Moderate-from points, `H` = High-from points (line 3: "Settings = Moderate from / High from"). M1H4 = today's setting (reproduces `a3_state`, line 6); M2H4 = Moderate needs 2 points; M1H3 = High from 3 points; M2H3 = both. Detail files named in line 3: `results_cc_60_180.md`, `results_rl_60_180.md`. Follows handoffs 1-51 (the A3 state counts here match the `v2_minus1` variant rows in handoff 51: CC low 3,918 / moderate 12,731, not the 3,920 / 12,729 of handoff 51's distribution table).
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photos overlap and are merged into source lines 1-59. Photo-to-line map (in the order sent): photo 1 = lines 1-35; photo 2 = lines 1, 19, 28-59. Line 59 is the last line shown (blank).
- Source lines are hard-numbered in the editor. Headings on lines 15, 19, 33, 42 and 51 come directly after a content line, with no blank line before them, as numbered. Lines 2-3, 16-18, 32 and 52-58 are long lines the editor shows as one numbered line each.
- **The Mac link was down when I wrote this, so this file was written in the cloud workspace and sent to chat only.** Copy it to `~/Python/Collections/pics/claude_code_handoff_52.md`, or ask me to commit it when the link is back.

---

## `summary.md` (lines 1-59)

````
1   # A3 threshold what-if — summary (2026-11-09)
2   Source: `crx_<p>_a3_check_payments`, latest month 2026-08-31, one row per account. CC `cc_60_180` n = 19,292; RL
3   `rl_60_180` n = 3,985. Settings = Moderate from / High from. Detail: `results_cc_60_180.md`, `results_rl_60_180.md`.
4
5   ## Sanity check
6   M1H4 reproduces `a3_state` on **every row** for both models (CC 19,292 / RL 3,985). The what-if is comparable with today.
7
8   ## State distribution (% of all rows; Unknown never moves)
9   | State | CC M1H4 | M2H4 | M1H3 | M2H3 | RL M1H4 | M2H4 | M1H3 | M2H3 |
10  |---|---:|---:|---:|---:|---:|---:|---:|---:|
11  | High | 1.3 | 1.3 | 3.6 | 3.6 | 1.6 | 1.6 | 8.1 | 8.1 |
12  | Moderate | 66.0 | 14.5 | 63.7 | 12.2 | 66.4 | 24.0 | 59.9 | 17.6 |
13  | Low | 20.3 | 71.8 | 20.3 | 71.8 | 25.2 | 67.6 | 25.1 | 67.5 |
14  | Unknown | 12.4 | 12.4 | 12.4 | 12.4 | 6.9 | 6.9 | 6.9 | 6.9 |
15  ## Points (no refusal) — why the settings behave this way
16  Exactly one point is the biggest group: CC 9,940 (53.9% of non-refusal rows), RL 1,689 (44.4%). Today these are all
17  Moderate; M2 sends **all** of them to Low. Exactly three points: CC 446, RL 259; M1H3 lifts **all** of them to High.
18  Refusal rows (CC 512 at 1 point, RL 98) are Low in every setting, so M2 does not touch them.
19  ## Crosstabs (n, % of all rows)
20  | M1H4 → M2H4 | CC | RL |
21  |---|---:|---:|
22  | Moderate → Low | 9,940 (51.5%) | 1,689 (42.4%) |
23  | Moderate stays | 2,791 (14.5%) | 956 (24.0%) |
24  | High, Low, Unknown unchanged | 255 / 3,918 / 2,388 | 62 / 1,004 / 274 |
25
26  | M1H4 → M1H3 | CC | RL |
27  |---|---:|---:|
28  | Moderate → High | 446 (2.3%) | 259 (6.5%) |
29  | Low → Moderate | <10 | <10 |
30  | Everything else unchanged | | |
31
32  The few Low → Moderate rows are refusal rows with 3 points (High under H3, minus one rung).
33  ## Who moves Moderate → Low under M2H4 (each is exactly 1 point)
34  | Combination (commitments / payments while delinquent / record before) | CC n (%) | RL n (%) |
35  |---|---:|---:|
36  | Thin promises, no payment, clean record: the record is the only evidence | 8,436 (84.9%) | 1,006 (59.6%) |
37  | Thin promises, some payment, not clean: one payment is the only evidence | 580 (5.8%) | 542 (32.1%) |
38  | Thin promises, some payment, no record | 228 (2.3%) | 99 (5.9%) |
39  | Broken promises, some payment, clean record (-1 +1 +1) | 345 (3.5%) | 12 (0.7%) |
40  | Broken promises, regular payment, not clean or no record (-1 +2) | 306 (3.1%) | 12 + <10 |
41  | Partly kept promises, no payment, not clean or no record | 45 (0.5%) | 15 + <10 |
42  ## Who moves Moderate → High under M1H3 (each is exactly 3 points)
43  | Combination | CC n (%) | RL n (%) |
44  |---|---:|---:|
45  | Thin promises, regular payments while delinquent, clean record | 211 (47.3%) | 138 (53.3%) |
46  | Partly kept promises, some payment, clean record | 151 (33.9%) | 47 (18.1%) |
47  | Partly kept promises, regular payments, not clean record | 49 (11.0%) | 47 (18.1%) |
48  | Partly kept promises, regular payments, no record | 18 (4.0%) | <10 |
49  | Kept promises, no payment, clean record | 11 (2.5%) | <10 |
50  | Kept promises, some payment, not clean or no record | <10 | 14 + <10 |
51  ## Reading
52  - M2 is a large change: Moderate falls from about two thirds of rows to 14.5% (CC) and 24.0% (RL). Over 85% of the CC
53    movers are one group: customers with a clean pre-delinquency record who made no promises and no payment since.
54    Whether that group is Moderate or Low is the decision. For RL, a third of the movers made some payment but have
55    a not-clean record.
56  - M1H3 is small for CC (+2.3 points of High) and larger for RL (+6.5), and about half of the movers pay regularly
57    while delinquent but have made no promises (thin).
58  - M2H3 is both effects added (they touch different point values). No recommendation here: facts for the decision.
59
````

## Notes on specific spots
- Sum checks that pass: state columns add to 100.0 (CC: 1.3 + 66.0 + 20.3 + 12.4; 1.3 + 14.5 + 71.8 + 12.4; 3.6 + 63.7 + 20.3 + 12.4; 3.6 + 12.2 + 71.8 + 12.4) and to 99.9-100.1 for RL by rounding. Line 22-24: CC 9,940 + 2,791 = 12,731 (today's Moderate) and 255 + 3,918 + 2,388 = 6,561, total 19,292; RL 1,689 + 956 = 2,645 and 62 + 1,004 + 274 = 1,340, total 3,985. Percentages: 9,940 / 19,292 = 51.5%, 1,689 / 3,985 = 42.4%; 446 / 19,292 = 2.3%, 259 / 3,985 = 6.5%. Line 16: 9,940 is 53.9% of the 18,435 non-refusal CC rows (19,292 minus 857 refusals, handoff 51) and 1,689 is 44.4% of 3,800.
- Mover tables: CC lines 36-41 add to 9,940 (8,436 + 580 + 228 + 345 + 306 + 45); the RL column adds to 1,689 once the hidden `<10` cells are counted (1,006 + 542 + 99 + 12 + 12 + 15 = 1,686, so the three `<10` cells hold 3 rows). Lines 45-50: CC 211 + 151 + 49 + 18 + 11 = 440, so the `<10` cell holds the other 6 of 446; RL 138 + 47 + 47 + 14 = 246, so the three `<10` cells hold the other 13 of 259. Shares as printed (211 / 446 = 47.3%).
- Line 9: the header repeats `M2H4 | M1H3 | M2H3` for RL after `RL M1H4`, as shown. Line 30: both cells are empty (`| Everything else unchanged | | |`), as shown.
- Lines 40-41 and 50: cells like `12 + <10` and `14 + <10` are as printed (a count plus a suppressed small cell).
- Line 56: "about half of the movers pay regularly while delinquent but have made no promises (thin)" matches lines 45 (47.3% CC / 53.3% RL).
- The `→` arrows and the em dashes on lines 1 and 15 are in the source as shown.
- OCR-risk digits: lines 11-14 (percentages), 16-18, 22-24, 28, 36-41, 45-50.
