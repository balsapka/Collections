# A2: update the model workbook for GRR's 180+ change

Give this to the UAT Sonnet 5.5 after bundle 10 is applied. It edits your workplace copy of
`a2_locatability_reference.xlsx`, the latest version (your edits and results stay). No PROD step.

````text
Goal: GRR accepted the A2 locatability logic with one change, and the model workbook
a2_locatability_reference.xlsx must say so. You work in UAT on the user's own copy, which is the
latest version: it holds their edits and results. Change only the text that describes this rule.

The decision: Non-Reachable needs the last 3 failed call days at 61–180 DPD and the last 6 at
180+ DPD. Everything else in the rule is unchanged: every one of those days failed, the oldest is
within the window (3 months at 61–180, 6 at 180+), no confirmed contact since. Code: GONE_DARK_DAYS
and gone_dark_days in a2_locatability/signals.py (bundle 10). 61–180 results do not change, and no
180+ results exist yet.

Edits (the user has changed some wording, so find each by meaning, and keep their wording around
the change):
- Logic, what Non-Reachable means: the last 3 days we called (6 at 180+) all failed, with no
  confirmed contact since.
- Logic, inputs: rename "Last 3 call days" to "Last call days"; meaning: the 3 most recent days we
  called (6 at 180+), each failed or not.
- Logic, Reachability rules, first rule: last 3 call days (6 at 180+) all failed, the oldest within
  the window, and no confirmed contact since.
- Logic, Parameters, "Failed call days": value = the last 3 call days at 61–180 DPD, the last 6 at
  180+ DPD. Why = add that 6 at 180+ was set by GRR, and make clear the existing call-day share
  and sensitivity text are about 61–180.
- Changes, Reachable row, "Now": 3 failed call days after a contact (6 at 180+) still make
  Non-Reachable.
- Changes: add one row after "Call minimum". Area "Failed call days at 180+"; Before "3 call days";
  Now "6 call days (GRR); 3 at 61–180"; Effect "None at 61–180; 180+ not run yet". Copy the
  formats of the row above.
- Any other place that states the 3-day streak as applying to all segments (Overview included):
  fix it the same way, and list it in your report.
- Leave as they are: the Examples sheet (its 3-day cases are 61–180 examples) and every Results
  sheet, whatever they say about call days.

Hard rules:
- Find cells by sheet and text, never by fixed address. Use openpyxl, without data_only, so
  formulas stay. Back the file up outside the repo before you save, and before saving check
  whether it has charts, images, pivot tables or anything else openpyxl would lose; if so, stop
  and tell the user.
- If a rule's text no longer matches what is described here, or the user's wording changes its
  meaning, do not overwrite it: leave it and ask the user.
- No pipeline code, no data, no customer rows. Commit the workbook only if the user says so.

Deliverables:
1. The saved workbook.
2. Reopen it and diff every cell's value and formula, on every sheet, against the file before your
   edit: only the cells you meant to change may differ, and every Results sheet must be identical.
3. A short report: each changed cell (sheet, old text, new text), the diff result, and any
   question for the user.
````
