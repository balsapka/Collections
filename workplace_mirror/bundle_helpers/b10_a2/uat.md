**Workbook (UAT Sonnet).** Your copy of `a2_locatability_reference.xlsx` has your own edits, so ask
the UAT Sonnet to make these text edits; find the cells by their text, change nothing else, reopen
and diff, and commit only if you say so:

- Logic, state meaning of Non-Reachable: "The last 3 days we called (6 at 180+) all failed, with no confirmed contact since."
- Logic, inputs: "Last 3 call days" → "Last call days", meaning "The 3 most recent days we called (6 at 180+), each failed or not."
- Logic, Reachability rule 1: "Last 3 call days (6 at 180+) all failed, the oldest within the window, and no confirmed contact since."
- Logic, Parameters, Failed call days: value "The last 3 call days at 61–180 DPD, the last 6 at 180+ DPD."; why "Fewer is not a pattern; 6 at 180+ set by GRR. 86% of accounts at 61–180 have 6+ call days in 3 months; sensitivity 1–10 days under check."
- Changes, Reachable row, Now: "A contact within the window; 3 failed call days after it (6 at 180+) still make Non-Reachable."
