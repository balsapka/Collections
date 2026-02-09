---
description: Process a single source document (auto-detects type and routes to correct analysis)
argument-hint: file-path
allowed-tools: Bash, Read, Glob, Grep, Write
---

Process the file at `$ARGUMENTS` for the Collections Risk Modeling project.

## Step 1: Detect file type and read it

Read the file. Based on the extension, determine the analysis type:

- `.pdf`, `.docx` → **Policy analysis** (extract DPD buckets, rules, actions, then analyze for DS implications)
- `.eml` → **Email distillation** (structured summary of stakeholder thread)
- `.xlsx`, `.csv` → **Data profiling** (schema, quality, feature potential, gaps)
- `.md`, `.txt` → **Meeting notes summarization** (key points, insights, data signals, follow-ups)

## Step 2: Perform the analysis

Use the corresponding agent's instructions to analyze the content. The agents are defined in `.claude/agents/`:

- `policy-analyzer.md` for policy docs
- `email-distiller.md` for emails
- `data-profiler.md` for data files
- `notes-summarizer.md` for meeting notes

## Step 3: Write output

Generate a timestamp with `date +%Y%m%d_%H%M%S` and write the analysis to `output/` using this naming:

- Policy docs → `output/policy_extract_{source_filename}_{timestamp}.md`
- Emails → `output/email_summary_{source_filename}_{timestamp}.md`
- Data files → `output/data_profile_{source_filename}_{timestamp}.md`
- Notes → `output/notes_summary_{source_filename}_{timestamp}.md`

Add a metadata comment at the top of the output:
```
<!-- Agent: {agent_type} | Source: {filename} | Generated: {timestamp} -->
```

## Step 4: Present key findings

After writing the file, present a concise summary of the most important findings to the user.
