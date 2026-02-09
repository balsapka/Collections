---
description: Process all unprocessed source files in data/
allowed-tools: Bash, Read, Glob, Grep, Write
---

Batch-process all source documents in `data/` that haven't been analyzed yet.

## Step 1: Inventory

List all files in `data/` (excluding `.gitkeep`). For each file, note the extension and what agent type it maps to:
- `.pdf`, `.docx` → policy-analyzer
- `.eml` → email-distiller
- `.xlsx`, `.csv` → data-profiler
- `.md`, `.txt` → notes-summarizer

## Step 2: Check what's already processed

List all files in `output/`. A source file is "already processed" if an output file exists whose name contains the source filename stem. List which files are new vs. already done.

## Step 3: Process new files

For each unprocessed file, perform the analysis as described in the corresponding agent definition (`.claude/agents/`). Write output to `output/` with the naming convention:
- `output/{type}_{source_filename}_{timestamp}.md`

Use `date +%Y%m%d_%H%M%S` for the timestamp. Add metadata comment at top of each output.

## Step 4: Summary table

Present a table showing:
| File | Type | Status | Key Finding |
|------|------|--------|-------------|

Where Status is "Processed (new)" or "Already existed" and Key Finding is a one-line highlight from each newly processed document.
