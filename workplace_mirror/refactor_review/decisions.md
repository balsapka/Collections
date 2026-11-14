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
