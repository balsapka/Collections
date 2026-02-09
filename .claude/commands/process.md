Process a single source document (auto-detects type and routes to correct analysis).
Argument: file path.

Process the file at `$ARGUMENTS` for the Collections Risk Modeling project.

## Step 1: Detect file type and read it

Read the file. Based on the extension, determine the analysis type:

- `.pdf`, `.docx` → **Policy analysis** (extract DPD buckets, rules, actions, then analyze for DS implications)
- `.eml` → **Email distillation** (structured summary of stakeholder thread)
- `.xlsx`, `.csv` → **Data profiling** OR **QnA extraction** (see detection logic below)
- `.md`, `.txt` → **Meeting notes summarization** (key points, insights, data signals, follow-ups)

**Excel/CSV detection**: Read the first row (headers) of the file. If columns match a QnA pattern (containing words like "Dimension", "Question", "Response", "Clarification" or similar), route to **qna-extractor**. Otherwise, route to **data-profiler**.

## Step 2: Perform the analysis

Use the corresponding agent's instructions to analyze the content. The agents are defined in `.claude/agents/`:

- `policy-analyzer.md` for policy docs
- `email-distiller.md` for emails
- `data-profiler.md` for raw data files
- `qna-extractor.md` for QnA structured Excel sheets
- `notes-summarizer.md` for meeting notes

## Step 3: Write output

Generate a timestamp with `date +%Y%m%d_%H%M%S` and write the analysis to `output/` using this naming:

- Policy docs → `output/policy_extract_{source_filename}_{timestamp}.md`
- Emails → `output/email_summary_{source_filename}_{timestamp}.md`
- Data files → `output/data_profile_{source_filename}_{timestamp}.md`
- QnA sheets → `output/qna_extract_{source_filename}_{timestamp}.md`
- Notes → `output/notes_summary_{source_filename}_{timestamp}.md`

Add a metadata comment at the top of the output:
```
<!-- Agent: {agent_type} | Source: {filename} | Generated: {timestamp} -->
```

## Step 4: Present key findings

After writing the file, present a concise summary of the most important findings to the user.
