# Council run 2 (A3 + A1): decisions

| ID | Date | Decision | Who |
|---|---|---|---|
| D-P-1 | 2026-11-13 | Bundle 25 = D-A3-29 + the refactor on top; the old bundle 25 was never built or run. Promise points, deadline, 180+ cut-offs and RL dispute codes stay out (undecided). | user |
| D-P-2 | 2026-11-13 | Any code may be edited; the focus is A3 and A1. | user |
| D-P-3 | 2026-11-13 | CASA features: reviewed, changes go to the workplace Sonnet as one prompt (`casa_handoff.md`). | user |
| D-P-4 | 2026-11-13 | Dead candidates are deleted if S7 confirms them and the user approves the list. | user |
| D-P-5 | 2026-11-13 | Run 1's rubrics and scorecard reused as frozen; "Fits A3 easily" is read as "fits the pending A3 / A1 rule changes easily". | Master (default, open at U0) |
| D-P-6 | 2026-11-13 | D-A3-29 coded before the baseline (`995a212`): the fold uses each follow-up row's own cutoff, as the spec says; a run matched to a plan still takes the plan's date and deadline. | Master, spec |
| D-0-1 | 2026-11-14 | Baseline accepted: oracle 188 datasets in 23 runs, pass (Master re-run, 153 s); smoke fails with the six `cc_raw_extract` import lines only; ruff 101 findings; spec tests pass. | Master |
| D-0-2 | 2026-11-14 | Oracle checkpoints every node output and runs in UTC (2 GB driver stalled in GC without it). | Cartographer |
| D-0-3 | 2026-11-14 | Dead list for U0: `_spine_utils.py`, `rl_a4_spine/`, `rl_spell_table/`, and `cc_spell/` with `build_cc_limits` / `crx_cc_limits`. The mirror cannot rule out workplace-only readers: a UAT grep is needed first (`inventory.md` §6). | Cartographer |
| D-U0 | 2026-11-14 | U0 approved: scope, reused rubrics (frozen); round 1 starts. Dead-code deletions are held until the workplace grep (`inventory.md` §6) is back. | user |
| D-1-1 | 2026-11-14 | Round 1 merge accepted (`e677655..ada44fa`): S7 B-01/02/03/05; S1-01..09; S3-02/04/09/10; S2-01/02/04/05/07/08/09/10/11; S4-01/02/03/05/07/08/10/11/13/14/15. Master re-ran the oracle: pass, 188 datasets. | Master |
| D-1-2 | 2026-11-14 | Pylint gate read as "no new message" for files whose only messages are imports the mirror cannot resolve (`a3_credibility/sources.py`, `cc_raw_extract/nodes.py`, `prm_products.py`): fewer statements make the same messages weigh more. | Master |
| D-1-3 | 2026-11-14 | S2-10 (`_latest_in_month` as `max(struct(day, value))`) kept but flagged: when a key has two rows on its latest day the old `row_number` pick was arbitrary and the new one takes the larger value. Within the old rule's possible outputs, but PROD zero-difference could show it: Q-R-09, and R-O to rule. | Master |
| D-1-4 | 2026-11-14 | Skipped at merge: S3-03 (after S1-01 every A1 node takes `params:crx_persona`), S3-07 (done by S1-05). Reverted: S4-04 (pylint R0914 on `create_a3_pipeline`). Held for reviewers: S3-01, S3-11, S2-12, S4-06, S4-16. Held for the user: S7 A-01, B-04, B-06, S2-03. | Master |
