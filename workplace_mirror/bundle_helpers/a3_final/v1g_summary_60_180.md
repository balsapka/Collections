# Handoff 54: `tmp_validation/a3_v1g/summary_v1g.md` lines 1-73 (A3 V1g: next statement (G) vs fixed 30 days (F) as the deadline of a promise event) (3 photos), 2026-11-09

## Context for Claude Code
- Source: 3 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest`, workspace `retail.collections.risk_profiling`). Tabs: `pipeline_registry.py`, `summary_v1g.md` (U = untracked, active). Path `tmp_validation > a3_v1g > summary_v1g.md`, breadcrumb `# A3 V1g summary - next statement (G) vs fixed 30 days (F) as the deadline of a promise event`. Status bar: Ln 1, Col 1, Spaces: 2, UTF-8, LF.
- Content: the V1g follow-up to V1f (handoff 53): compares two deadlines for a promise event, G = next statement and F = fixed 30 days, for `cc_60_180` | `rl_60_180` (CC | RL separated by `|`, as in line 7). Evidence files named in line 3: `results_v1g_cc_60_180.md`, `results_v1g_rl_60_180.md`. 180+ not run. Verdict (lines 52-72): F, not G, at 60-180. Follows handoffs 1-53.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photos overlap and are merged into source lines 1-73. Photo-to-line map (in the order sent): photo 1 = lines 1, 9, 46-73; photo 2 = lines 1, 9, 32-65; photo 3 = lines 1-36. Line 73 is the last line shown (blank); I can't tell whether the file continues.
- Source lines are hard-numbered in the editor. Bullets and the verdict paragraph are one source paragraph each, but the editor numbers every wrapped visual line, so the text is kept exactly as numbered.
- **The Mac link was down when I wrote this, so this file was written in the cloud workspace and sent to chat only.** Copy it to `~/Python/Collections/pics/claude_code_handoff_54.md`, or ask me to commit it when the link is back.

---

## `summary_v1g.md` (lines 1-73)

````
1   # A3 V1g summary - next statement (G) vs fixed 30 days (F) as the deadline of a promise event
2
3   Evidence: `results_v1g_cc_60_180.md`, `results_v1g_rl_60_180.md` (month 2026-08-31, prediction base
4   2026-05-31). **180+ not run (cc_180_plus, rl_180_plus): the 180+ questions are unanswered.**
5   Baseline = the real output (`a3_kept_by` = payments; recomputed points equal the persisted ones on
6   100 %); refusal flag now present (844 CC, 185 RL accounts). Moderate from 2, High from 4. Format:
7   CC | RL.
8
9   ## One line per question (cc_60_180 | rl_60_180)
10  - **Q1** events 14,264 | 2,330 = matched 3,836 / table-only 3,706 / follow-up only 6,722 | 653 / 335
11    / 1,342; 7,421 | 190 unmatched A1 events dropped (A1 left: 538 | 10, all matched). Accounts with
12    >= 1 concluded event: G 29.2 % | 26.3 %, F 28.3 % | 23.6 %, against 24.0 % | 14.0 % for bundle 17
13    instalments. Leave Thin: G 7.5 % | 8.8 %, F 7.8 % | 9.3 %. G has no statement after the event for
14    6.4 % of CC events (fallback); the amount equals V1f's wherever both exist (CC 0 differ; RL
15    0.8 %).
16  - **Q2** paid / partial / none, same events (12,903 | 2,042): G 30.0 / 4.2 / 65.8 | 38.7 / 17.5 /
17    43.8; F 40.6 / 6.9 / 52.5 | 61.5 / 14.2 / 24.3. G paid is nearly a subset of F (paid under G, not
18    F: < 10 | 0); F-paid-not-G 1,371 | 466. CC G paid by days to the statement 15.1 / 34.0 / 37.4 /
19    37.4 % (1-7 / 8-14 / 15-21 / 22-31) vs F 37.2 / 44.3 / 42.4 / 39.1 %. CC events <= 7 days before a
20    statement (3,763): 15.1 % paid by the statement, 37.2 % in 30 days, 22.1 % only in the next cycle.
21    RL G paid by day of month 39.1 / 41.8 / 34.4 / 39.0 % (flat); 58 % of events fall after the 15th.
22    By class CC (G | F paid): P1 31.4 | 40.5, P2 24.0 | 31.9, T-PTP 20.5 | 32.9, T-SET 38.3 | 56.8,
23    A1 40.6 | 55.9; follow-up only 33.7 | 41.2 vs matched 24.0 | 35.8. RL follow-up only 37.1 | 60.1.
24  - **Q3** paid events whose payment window meets a B qualifying cycle, G: recent 100 % | 99 %, older
25    0 % (by B's window) but 99.9 % | 100 % at any age: same rule, same money. F: recent 93.5 % | 76 %.
26    Paid events older than B's window: G 71 % | 76 %, F 70 % | 68 %. Kept & B none / Broken & B
27    regular, G 0.2 % / 1.9 % | 0.4 % / 1.0 %; F 0.6 % / 1.1 % | 0.7 % / 0.4 %; bundle 17 0.1 % /
28    3.9 % | 0.3 % / 0.4 %.
29  - **Q4** Kept / Partly / Thin / Broken, bundle 17 | G | F: CC 1.1 / 3.5 / 84.0 / 11.4 | 1.2 / 6.8 /
30    81.8 / 10.2 | 2.3 / 8.6 / 81.1 / 7.9; RL 1.8 / 6.1 / 90.1 / 2.0 | 2.3 / 6.8 / 83.5 / 7.4 | 5.3 /
31    8.2 / 82.9 / 3.6. State High: CC 1.4 -> 2.3 (G) / 3.4 % (F); RL 1.6 -> 2.2 / 3.6 %. Moderate: CC
32    14.8 -> 15.6 / 16.4 %; RL 24.0 -> 22.1 / 23.9 %.
33  - **Q5** roll share among accounts with a later level, Kept / Partly / Thin / Broken. CC: G 59.6 /
34    64.6 / 92.0 / 78.0, F 62.4 / 63.1 / 92.7 / 81.1, bundle 17 28.4 / 68.7 / 92.9 / 65.3. RL: G 50.0 /
35    65.0 / 78.8 / 65.6, F 61.2 / 65.8 / 78.2 / 71.7, bundle 17 65.2 / 71.2 / 76.2 / 67.3. No later
36    level: 39.7 % CC (6,314), 0.3 % RL (10), the same in every row; CC cured = 0.
37
38  AUC non-roll vs roll (ladder Thin 3rd | ladder Thin last | state):
39
40  | AUC | CC ladder A | CC ladder B | CC state | RL A | RL B | RL state |
41  |---|---|---|---|---|---|---|
42  | G | 0.550 | 0.676 | 0.714 | 0.521 | 0.572 | 0.578 |
43  | F | 0.624 | 0.701 | 0.740 | 0.548 | 0.559 | 0.588 |
44  | bundle 17 | 0.435 | 0.713 | 0.686 | 0.510 | 0.517 | 0.565 |
45
46  Baseline points, roll share 0 / 1 / 2 / 3 / 4+: CC 95.0 / 90.6 / 73.8 / 62.9 / 33.5 % (< 0: 87.4);
47  RL 86.4 / 72.5 / 68.8 / 59.2 / 58.2 %. Refusal on: 92.7 % | 84.7 % roll vs 86.6 % | 75.2 % off.
48  - **Q6** settlement instalments paid (concluded): G 32.9 % of 8,369 | 52.5 % of 242; F 53.7 % of
49    7,642 | 73.6 % of 159. Plans with all instalments paid: G 11.8 % | 34.0 %, F 21.2 % | 56.7 %;
50    none paid: G 42.3 % | 32.1 %, F 24.2 % | < 10. CC matched vs table-only plans differ by 1-5 pts.
51
52  ## Verdict
53  At 60-180, F, not G. On ranking (Q5), F has the higher AUC on the state in both products (CC 0.740
54  vs 0.714, RL 0.588 vs 0.578) and on the ladder with Thin third (0.624 vs 0.550, 0.548 vs 0.521);
55  Thin last gives CC F 0.701 vs G 0.676, RL G 0.572 vs F 0.559. The RL gaps (0.01-0.03 on about 3,100
56  accounts) are probably noise (no intervals computed); the CC gaps are larger. G's coverage edge is
57  real but small (CC 29.2 vs 28.3 % of accounts, RL 26.3 vs 23.6 %; G concludes events earlier), and F
58  leaves Thin as often or more (7.8 vs 7.5 %, 9.3 vs 8.8 %). G is also biased by the window: a CC
59  promise made within 7 days of a statement is paid by it 15 % of the time, and 22 % of those are
60  paid in the next cycle, so G calls them broken; RL G is the event month's cash, which can include
61  cash before the promise (day-level sources exist, see below). Overlap with B is structural under
62  G (every recent paid event shares B's qualifying cycle, 100 % CC); F is lower (93.5 % | 76 %) and
63  shows more Kept-but-no-B accounts (0.6-0.7 %), though both are small. In both, 68-76 % of paid
64  events are older than B's window, which is where Dimension A could add information. Against bundle
65  17: neither is a clear win. The state AUC rises by 0.05 (CC) and 0.02 (RL) with F, and the extra
66  accounts with evidence are real, but in CC bundle 17's Kept is much purer (roll 28 % vs 60 % G,
67  62 % F), so one month's due per event dilutes Kept; in RL the new Kept is the purer one (G 50 %,
68  F 61 % vs 65 %). With Thin last bundle 17 is level in CC (0.713 vs 0.701). Thin remains the
69  worst-rolling level everywhere, so it must not be read as neutral. 180+ was not run, so nothing
70  is decided there; run it before choosing. Day-level RL repayment data exist
71  (`ec_account_loan_transaction.la_txn_dt` and amounts, `sa_account_loan_dmd`), which would remove
72  RL's month-level problem; not tested.
73
````

## Notes on specific spots
- Sum checks that pass: Q1 3,836 + 3,706 + 6,722 = 14,264 (CC) and 653 + 335 + 1,342 = 2,330 (RL); Q2 paid / partial / none triples add to 100 (30.0 + 4.2 + 65.8; 38.7 + 17.5 + 43.8; 40.6 + 6.9 + 52.5; 61.5 + 14.2 + 24.3); Q4 level splits add to 100 (CC bundle 17 1.1 + 3.5 + 84.0 + 11.4; G 1.2 + 6.8 + 81.8 + 10.2; F 2.3 + 8.6 + 81.1 + 7.9 = 99.9; RL 1.8 + 6.1 + 90.1 + 2.0; 2.3 + 6.8 + 83.5 + 7.4; 5.3 + 8.2 + 82.9 + 3.6). The verdict numbers match the AUC table and Q1/Q3/Q5: state AUC CC 0.740 vs 0.714, RL 0.588 vs 0.578; ladder Thin third 0.624 vs 0.550 and 0.548 vs 0.521; Thin last CC 0.701 vs 0.676, RL 0.572 vs 0.559; bundle 17 state 0.686 / 0.565, so "rises by 0.05 (CC) and 0.02 (RL)" holds (0.054 and 0.023); coverage 29.2 vs 28.3 % and 26.3 vs 23.6 %; Thin 7.8 vs 7.5 % and 9.3 vs 8.8 %; Kept roll 28 vs 60 / 62 % (CC) and 50 / 61 vs 65 % (RL); bundle 17 vs F with Thin last 0.713 vs 0.701.
- Possible mismatch with earlier handoffs: line 6 says the refusal flag is present on 844 CC and 185 RL accounts; handoff 51 (`a3_refusal_flag`, a different run) has 857 CC and 185 RL. RL matches, CC differs by 13; copied as shown.
- Line 31: `State High: CC 1.4 -> 2.3 (G) / 3.4 % (F)` starts from 1.4 % (today's High under this baseline); handoff 53 (V1f) had 1.3 % -> 2.9 %; different base, as printed.
- Line 41: the separator row has seven dash groups for the seven header columns, as shown (no `:` alignment marks, unlike handoff 51-52).
- Line 47: `Refusal on: 92.7 % | 84.7 % roll vs 86.6 % | 75.2 % off.` is as printed; the baseline points line (46) has `(< 0: 87.4)` for CC only.
- Line 4: `**180+ not run (cc_180_plus, rl_180_plus): the 180+ questions are unanswered.**` is bold in the file.
- Line 18-19: CC G paid by days to the statement `15.1 / 34.0 / 37.4 / 37.4 %` for `1-7 / 8-14 / 15-21 / 22-31`; the 37.4 appears twice, as printed.
- Line 55: "about 3,100 accounts" is the file's wording for the RL sample.
- OCR-risk digits: nearly every number in lines 10-50, especially Q2 (16-23), Q4 (29-32), Q5 (33-36), the AUC table (42-44) and the verdict AUC values (53-68).
