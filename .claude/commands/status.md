Show pipeline status — what's been processed, what's pending, what's stale.

Show the current state of the Collections document processing pipeline.

## 1. Source Files

List all files in `data/` with their type, size, and last-modified date. Classify each by the agent that would process it:
- `.pdf`/`.docx` → Policy
- `.eml` → Email
- `.xlsx`/`.csv` → Data or QnA (check headers for Dimension/Question/Response/Clarification pattern)
- `.md`/`.txt` → Notes

## 2. Processed Outputs

List all files in `output/` grouped by type (policy_extract, policy_analysis, email_summary, data_profile, qna_extract, notes_summary, project_brief, gap_analysis). For each, show filename, timestamp, and size.

## 3. Coverage Check

Cross-reference: which source files in `data/` have corresponding outputs in `output/`, and which don't? Flag any unprocessed source files.

## 4. Staleness Check

If a `project_brief_*.md` exists, check whether any agent output is newer than the brief. If so, flag that the brief is stale and should be regenerated with `/project:brief`.

## 5. Suggested Next Steps

Based on the above, suggest what the user should do next:
- "3 files in data/ haven't been processed — run `/project:batch`"
- "Brief is out of date — run `/project:brief`"
- "All documents processed, ready for gap analysis — run `/project:gaps`"
- etc.
