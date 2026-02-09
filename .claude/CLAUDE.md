# Collections Risk Modeling — Document Distillation Pipeline

## Project Purpose

This project helps a data science team working with a Middle East bank's **Group Retail Risk** department. The bank needs a classifier model (Low/Medium/High risk) for delinquent customers within 60+ DPD (Days Past Due) buckets. The core challenge is that late-stage buckets have "dry" data — cards are blocked, no transactions — so customer profiling must rely on pre-delinquency history and potentially synthetic data.

## How This Repo Works

Raw source documents (policy PDFs, email threads, Excel data files, meeting notes) are placed in `data/`. Claude Code processes them directly via agents and slash commands. All outputs are saved as timestamped markdown files in `output/`.

### Agents (subagents Claude Code can delegate to)

1. **policy-analyzer** — Multi-pass extraction + analysis of collections policy docs (primary agent)
2. **email-distiller** — Summarizes stakeholder email threads
3. **data-profiler** — Profiles Excel/CSV data files for ML readiness
4. **qna-extractor** — Distills stakeholder Q&A sheets (Dimension/Question/Response/Clarification format)
5. **notes-summarizer** — Distills free-form meeting/discussion notes into insights
6. **synthesizer** — Combines all outputs into a single project brief

### Slash Commands

| Command | What it does |
|---------|-------------|
| `/project:process <file>` | Process a single file (auto-detects type, routes to correct agent) |
| `/project:batch` | Process all unprocessed files in `data/` |
| `/project:status` | Show pipeline dashboard — what's processed, what's pending, what's stale |
| `/project:brief` | Generate/refresh the consolidated Data Science Project Brief |
| `/project:context` | Load all project context (use at start of new sessions) |
| `/project:gaps` | Find contradictions and gaps across all processed documents |

## Directory Layout

```
data/              — Drop source documents here (PDFs, emails, Excel, notes)
output/            — Agent outputs (timestamped markdown files)
.claude/agents/    — Claude Code subagent definitions
.claude/commands/  — Custom slash commands
```

## Domain Terminology

- **DPD**: Days Past Due — how many days a payment is overdue
- **Bucket**: A DPD range (e.g. 1-30, 31-60, 61-90)
- **Cure**: When a delinquent customer returns to current status
- **Roll**: When a customer moves from one DPD bucket to a worse one
- **Dry data**: Buckets where behavioral signals disappear (card blocked, no activity)
- **Murabaha/Tawarruq/Ijarah**: Islamic finance product types with distinct default handling
- **SAMA/CBUAE/CBB**: Central bank regulators (Saudi, UAE, Bahrain)

## Output Naming Convention

All outputs follow: `{type}_{source_filename}_{YYYYMMDD_HHMMSS}.md`

Types: `policy_extract`, `policy_analysis`, `policy_questions`, `email_summary`, `notes_summary`, `qna_extract`, `data_profile`, `project_brief`, `gap_analysis`
