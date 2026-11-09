# Handoff 53: `tmp_validation/a3_v1f/summary_v1f.md` lines 1-91 (A3 V1f: Dimension A as promise events judged by a sufficient payment) (3 photos), 2026-11-09

## Context for Claude Code
- Source: 3 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest`, workspace `retail.collections.risk_profiling`, branch `feature/persona_refactor*`). Tabs: `pipeline_registry.py`, `17_a3_credibility_engine.md`, `summary_v1f.md` (active), `summary.md`. Path `tmp_validation > a3_v1f > summary_v1f.md`, breadcrumb `# A3 V1f summary - Dimension A as promise events judged by a sufficient payment`. Blame "You, 2 minutes ago | 1 author (You)" and, on line 1, "You, 15 minutes ago"; status bar "You, 15 minutes ago", Ln 1, Col 1.
- Content: summary of the V1f variant of A3 Dimension A (promise events judged by a sufficient payment) for `cc_60_180` | `rl_60_180` (CC | RL separated by `|` throughout). Evidence files named in line 3: `results_v1f_cc_60_180.md`, `results_v1f_rl_60_180.md`. 180+ was not run. References "bundle 17" (the earlier A3 level logic), Dimensions B and C, and the promise-name groups P1/P2/P3 (promises), A1/A2 (agreements), R (retain), K (customer-paid names), I and N (see lines 64-70). Follows handoffs 1-52.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photos overlap and are merged into source lines 1-91. Photo-to-line map (in the order sent): photo 1 = lines 1-35; photo 2 = lines 1, 10, 31-64; photo 3 = lines 1, 52, 59-91. Line 91 is the last line shown (blank).
- Source lines are hard-numbered in the editor. Every bullet and paragraph below is one source line wrapped over several numbered lines as the editor numbers them (the number is on each visual line here, so the text is kept exactly as numbered).
- **The Mac link was down when I wrote this, so this file was written in the cloud workspace and sent to chat only.** Copy it to `~/Python/Collections/pics/claude_code_handoff_53.md`, or ask me to commit it when the link is back.

---

## `summary_v1f.md` (lines 1-91)

````
1   # A3 V1f summary - Dimension A as promise events judged by a sufficient payment
2
3   Evidence: `results_v1f_cc_60_180.md`, `results_v1f_rl_60_180.md` (month 2026-08-31; Q8 base
4   2026-05-31). **180+ not run.** Window = Dimension A's. Judge: payments in (event day, first
5   statement after it / end of next month] >= max(one month's due, 100 AED). Run caveats:
6   `a3_refusal_flag` was not in the strong-negative table (refusal demotion off in every state column);
7   the persisted commitments level exists for 78 CC accounts only (CC "persisted" column and its Q7
8   check are void; RL agrees with the recomputed level on 90.8 %).
9
10  ## One line per question (cc_60_180 | rl_60_180)
11  - **Q1** names: 154 | 142 distinct; 67 | 64 not in the table, none is a promise (see set). No P/A
12    name is logged after a payment (CC after 15-29 % vs before 4-9 %); K names are (before 39-69 %,
13    after 3-11 %); flag only REWRITE AGREED (n=46, before 24 %). All 4,984 CC PTP-category rows are
14    P1. RL cash is month-level, so its timing check says nothing (every name ~50 %).
15  - **Q2** events (latest month): 18,751 | 2,440 = matched 3,836 / table-only 3,706 / follow-up only
16    11,209 | 653 / 335 / 1,452. Follow-up -> nearest table record within 7 d: 25.8 % | 31.4 % (none
17    21.4 % | 31.7 %, >30 d 34.2 % | 21.3 %); table -> follow-up within 7 d: 55.1 % | 71.2 %. Accounts
18    with >= 1 event 33.5 % | 26.9 % vs 23.3 % | 14.0 % with a concluded instalment today (events per
19    account 0/1/2/3+: 66.5/13.4/7.2/12.9 | 73.1/13.4/6.1/7.4). 30 days: matched 3,836 -> 4,226 | 653
20    -> 656, accounts with an event unchanged (6,463 -> 6,425 | 1,073 -> 1,072), events fall to 13,194
21    | 1,862 (longer runs). The +/-7 d match is enough. R: 63 | 70 rows, none inside a run.
22  - **Q3** reference: first instalment due date = event day for 100 % of table events (7,542 | 988),
23    so (a) and (b) never differ (0.0 %). Table PTPs carry no promised date.
24  - **Q4** paid / partial / none: matched 23.9/4.7/71.4 | 59.5/14.9/25.7; table-only 28.9/3.8/67.3 |
25    66.8/13.0/20.2; **follow-up only 38.6/3.5/57.9 | 60.4/14.1/25.5**. By class CC: A1 46.2, P1 31.0,
26    P2 24.0, T-SET 36.6, T-PTP 20.1 % paid. Window length drives CC: 15.4 % paid at <= 7 d, 34.9 % at
27    8-14 d, 43.3 % at 15-30 d (27 % of events have <= 7 d). RL strict cash (months after the event day
28    only): 34.3 / 37.7 / 37.5 % paid, against 59-67 % in the main reading, so RL's paid rate is mostly
29    same-month cash. Settlement per instalment 61.9 % | 82.4 % paid; per plan all paid 24.3 % | 63.3
30    %. K name in grace: 84.2 % | 86.0 % paid vs 16.6 % | 50.0 % without.
31  - **Q5** held-or-improved 48.9 % | 34.8 % vs paid 33.7 % | 60.9 %; agree on 84.8 % | 68.3 %. CC paid
32    events never roll (0 of 5,876): the level is driven by the same payment, so Q5 is not independent
33    of Q4. No CC event is at the bucket-08 cap. cured = 0 in CC.
34  - **Q6** paid events whose payment cycle is also a B qualifying cycle: recent (cutoff inside B's
35    window) 100 % | 77.3 %, older 0 % | 0 % (by construction: same rule, B's window). 70 % | 67 % of
36    paid events are older (4,120 of 5,876 | 871 of 1,298). New A vs B: Kept & B none 47 (0.2 %) | 27
37    (0.7 %), all from older events (66 at CC "older"; 0 recent); Broken & B regular 384 (2.0 %) | 15
38    (0.4 %), 348 of them older. A vs C: Cramer's V 0.09 | 0.08, nothing.
39  - **Q7** (reading A) leave Thin: 1,522 (9.3 % of bundle 17's Thin) | 345 (9.6 %); **table events
40    only: 109 (0.7 %) | 28 (0.8 %)**, so the gain is the follow-up-only events. State High 1.3 % ->
41    2.9 % (B: 3.0 %) | 1.6 % -> 3.8 % (B: 4.1 %). Reading B changes ~1-2 % of levels. CC levels
42    disagree with bundle 17 (new Kept: 52.9 % are bundle-17 Broken): an event is a whole plan judged
43    on one month's due, bundle 17 judges each instalment's cumulative amount (my explanation, not
44    tested).
45  - **Q8** roll share by level (Kept / Partly / Thin / Broken): new A 46.6/63.9/93.5/78.4 |
46    60.8/65.8/78.3/71.9; bundle 17 28.4/68.7/92.9/65.3 | 65.2/71.2/76.2/67.3. Chance a non-roller is
47    ranked above a roller (ladder order Kept>Partly>Thin>Broken): new A 0.578 | 0.549, new B 0.582 |
48    0.547, bundle 17 0.435 | 0.510; re-ordering Thin last gives 0.726 | 0.561 (A), 0.715 | 0.517
49    (b17). Monotone check fails for all (Thin rolls most). Caveat: 6,314 | ~10 accounts have no level
50    at the later date and are left out (cure and exit are not separated).
51
52  ## Final promise set (window rows / agreements, latest month)
53  - **P1** (CC | RL): PROMISE TO PAY SCHEDULED 7,409 / 2,410 | 1,202 / 556; PROMISE TO PAY 4,454 /
54    2,529 | 697 / 434; DIGITAL COLLECT  PTP SUBSCRIBED 525 / 411 | 172 / 109; PTP PARTIALLY,
55    EOSB_PTP_DOCUMENTS <10.
56  - **P2**: CODE25 WILL PAY AT SALARY 4,534 / 2,175 | 481 / 268; WILL PAY AT SALARY <10. **P3**
57    SOFTPTP 35 / 32 | <10 (reported apart; 87 % none, n=31).
58  - **A1**: SETTLEMENT 7,493 / 1,924 | 174 / 80; BALCON WP 24/12/48 541/40/18; REWRITE AGREED 46;
59    BALCON WOP <10. Only 538 of 4,429 CC SETTLEMENT-dated events match a plan record: the name is
60    mostly not a plan.
61  - **A2** POST DATED CHEQUE AVAILABLE / COLLECTED: no rows for either model. **R** RETAIN PTP 63 |
62    70, adds nothing. **K** CUSTOMER MADE PAYMENT 6,266, ACCOUNT PAID 4,501, PARTIALLY PAID 2,180,
63    CLAIMS MADE PAYMENT 1,442 (CC); cross-check only.
64  - **Unmapped, proposed (no addition to the promise set):** SETTLEMENT INITIATED 972 / APPROVED 246 /
65    REJECTED 12 (LGL workflow, not a customer promise: I; APPROVED is the one GRR could class A1);
66    *CHEQUE BOUNCED, REWRITE REJECTED: N (<10); GUARANTOR ACCOUNT DEBITED: K (<10); REFERRED FOR
67    REWRITE/RESCHEDULE, REQUEST*, EOSB, AWAITING EOSB, RESTRUCTURE REQUEST APPROVED: I; call handling
68    (CALL CONNECTED 23,228, CALLBACK*, DISCONNECTED, VOICE_MAIL, LINE BUSY, LEFT MESSAGE*,
69    VOICE_ISSUE, ININ-*), situation (OUT OF COUNTRY, LEFT JOB, FRAUD/SKIP CASE), legal / vehicle,
70    documents, dunning: not about paying.
71
72  ## Verdict
73  Dimension A can be built from promise events judged by payment, and the follow-up names are worth
74  adding: they put 33.5 % (CC) and 26.9 % (RL) of accounts under evidence against 23 % and 14 %, and
75  9-10 % of bundle 17's Thin accounts gain a level, but only through follow-up-only events (table-only
76  events move 0.7-0.8 %). It is not reliable as specified. The CC paid rate is mostly an artefact of
77  the grace window (15 % at <= 7 days, 43 % at 15-30) and RL's is mostly same-month cash (59-67 % vs
78  34-38 % strict), so the follow-up-only vs matched comparison (CC 38.6 vs 23.9 %, RL 60.4 vs 59.5 %)
79  shows they are not worse than table plans, but not that either is a good promise: a fixed window
80  from the event day (e.g. 30 days) is needed. Table PTPs carry no promised date, and A1 `SETTLEMENT`
81  is mostly not a plan. The payment reading is the better one at 60-180: bucket movement agrees with
82  payment on 85 % (CC) but is the same payment seen through the delinquency level (paid events never
83  roll), so it adds no independent check; 180+ was not run and cannot be answered. Against Dimension B
84  the overlap is structural: every recent paid event shares B's qualifying cycle (CC), and A adds
85  information only through the 70 % of paid events older than B's window; there Kept with no B payment
86  is 0.2-0.7 % of accounts and Broken with regular B 0.4-2.0 %, small but real. As a predictor the
87  ladder is weak: Thin is worse than Broken, so the order must read Kept > Partly kept > Broken > Thin
88  (AUC 0.73 CC, 0.56 RL); new A beats bundle 17 on CC (0.73 vs 0.72, ladder 0.58 vs 0.44), not clearly
89  on RL. Recommend: keep follow-up events (P1, P2, A1 names with a plan, P3 apart), drop the ladder's
90  reading of Thin as neutral, fix the window, and run 180+ before deciding.
91
````

## Notes on specific spots
- Sum checks that pass: line 15-16: 3,836 + 3,706 + 11,209 = 18,751 (CC) and 653 + 335 + 1,452 = 2,440 (RL); line 22: 7,542 = 3,836 + 3,706 and 988 = 653 + 335 (table events); line 19: events per account 66.5 + 13.4 + 7.2 + 12.9 = 100.0 and 73.1 + 13.4 + 6.1 + 7.4 = 100.0; line 24-25: paid / partial / none triples add to 100 (23.9 + 4.7 + 71.4; 28.9 + 3.8 + 67.3; 38.6 + 3.5 + 57.9; 59.5 + 14.9 + 25.7 = 100.1; 66.8 + 13.0 + 20.2; 60.4 + 14.1 + 25.5); line 36: 4,120 / 5,876 = 70.1% and 871 / 1,298 = 67.1% (printed 70 % | 67 %); lines 74 vs 18: 33.5 / 26.9 vs 23.3 / 14.0 (printed "23 % and 14 %"); lines 47-48 vs verdict lines 87-88: ladder 0.578 -> "0.58", bundle 17 0.435 -> "0.44", re-ordered AUC 0.726 / 0.561 -> "0.73 CC, 0.56 RL", bundle 17 re-ordered 0.715 -> "0.72".
- Not checked against other data in the photos: the 4,984 CC PTP-category rows (line 13) vs the P1 rows (4,454 + 525 + the `<10` cells = about 4,984); the 4,429 CC SETTLEMENT-dated events (line 59) vs "SETTLEMENT 7,493 / 1,924" (line 58, window rows / agreements; different base).
- Line 54: `DIGITAL COLLECT  PTP SUBSCRIBED` has two spaces in the photo, as shown. Lines 58: `BALCON WP 24/12/48 541/40/18` is as printed (two triples).
- Lines 66-67: the `*` in `*CHEQUE BOUNCED`, `REQUEST*`, `CALLBACK*`, `LEFT MESSAGE*`, `ININ-*` is a wildcard in the source (name patterns), as shown; a leading `*` on line 66 is part of `*CHEQUE BOUNCED`.
- Lines 29-30: "63.3" at the end of line 29 and "%. K name..." at the start of line 30 is a wrap in the source as numbered.
- Line 39: "bundle 17's Thin" etc. is as printed; line 43-44 "(my explanation, not tested)" is part of the source text.
- Line 89: "drop the ladder's reading of Thin as neutral" is as printed (the source wording; the sentence reads as if the ladder's Thin reading is dropped, not that Thin is read as neutral).
- OCR-risk digits: almost every number in lines 11-50 (percentages with spaces before `%` as printed, counts like 18,751 / 11,209 / 6,314 / 7,409 / 23,228), the AUC / ladder values on lines 47-48, and the two-digit pairs `CC | RL`.
