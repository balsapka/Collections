# Collections Risk Modeling — Document Distillation Pipeline

## Project Purpose

This project helps a data science team working with a Middle East bank's **Group Retail Risk** department. The bank needs a classifier model (Low/Medium/High risk) for delinquent customers within 60+ DPD (Days Past Due) buckets. The core challenge is that late-stage buckets have "dry" data — cards are blocked, no transactions — so customer profiling must rely on pre-delinquency history and potentially synthetic data.

## How This Repo Works

Raw source documents (policy PDFs, email threads, Excel data files) are placed in `data/`. Four Claude Code agents process them:

1. **policy-analyzer** — Multi-pass extraction + analysis of collections policy docs (primary agent)
2. **email-distiller** — Summarizes stakeholder email threads
3. **data-profiler** — Profiles Excel/CSV files for ML readiness
4. **synthesizer** — Combines all outputs into a single project brief

Agents invoke Python scripts in `scripts/` which use the Anthropic API. Outputs go to `output/`.

## Directory Layout

```
data/           — Drop source documents here (PDFs, emails, Excel)
output/         — Agent outputs (timestamped markdown files)
scripts/        — Python runner scripts called by agents
src/prompts/    — LLM system prompts (one file per agent)
src/utils/      — Shared utilities (API client, file extraction, output writer)
.claude/agents/ — Claude Code subagent definitions
```

## Environment Requirements

- `ANTHROPIC_API_KEY` must be set in environment
- `CLAUDE_MODEL` optionally overrides default model (default: claude-sonnet-4-5-20250514)
- Python dependencies: `pip install -r requirements.txt`

## Domain Terminology

- **DPD**: Days Past Due — how many days a payment is overdue
- **Bucket**: A DPD range (e.g. 1-30, 31-60, 61-90)
- **Cure**: When a delinquent customer returns to current status
- **Roll**: When a customer moves from one DPD bucket to a worse one
- **Dry data**: Buckets where behavioral signals disappear (card blocked, no activity)
- **Murabaha/Tawarruq/Ijarah**: Islamic finance product types with distinct default handling
