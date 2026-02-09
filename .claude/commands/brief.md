Generate or refresh the consolidated Data Science Project Brief from all outputs.

Generate a consolidated Data Science Project Brief by synthesizing all agent outputs in `output/`.

## Step 1: Collect all outputs

Read every markdown file in `output/` (excluding existing `project_brief_*.md` files). Group them by type:
- `policy_extract_*` — Structural policy extractions
- `policy_analysis_*` — Data science analysis of policies
- `email_summary_*` — Email thread summaries
- `notes_summary_*` — Meeting notes summaries
- `data_profile_*` — Data file profiles
- `qna_extract_*` — Stakeholder Q&A extractions
- `gap_analysis_*` — Previous gap analyses (if any)

If no outputs exist, tell the user to process documents first with `/project:batch` or `/project:process`.

## Step 2: Synthesize into a project brief

Produce a single document with these sections:

# Data Science Project Brief: Group Retail Risk — Collections Classifier

## 1. Business Context
What the bank's collections process looks like today. Summarize the DPD workflow, key stages, and current pain points. 2-3 paragraphs max.

## 2. The Ask
What the business wants built — be precise about the classification task, target users, and how the output would be consumed.

## 3. The Real Problem
Why this is hard: the "dry data" problem in late-stage buckets, the lack of outcome labels, the need for customer profiling. Frame this as the core data science challenge.

## 4. Data Inventory
| Source | Contents | Quality | Key Features | Gaps |

## 5. Stakeholder Map
Key people, what they care about, and their influence on the project.

## 6. Modeling Strategy
Recommended approach, target variable design, feature sources, validation plan. Include the pre-delinquency profiling and synthetic data angle.

## 7. Data Requests
Prioritized list of what to ask the bank for, with justification.

## 8. Open Questions
Unresolved items that need business input before modeling can begin.

## 9. Risks & Dependencies
What could block or derail the project.

## 10. Recommended Next Steps
Concrete actions in priority order.

**Rules:**
- Resolve contradictions between sources — note them if unresolvable
- Be opinionated — recommend approaches, don't just list options
- Keep it under 2000 words — this is a brief, not a thesis
- Cross-reference sources: "(per policy doc)", "(per email thread)", "(per data profile)", "(per QnA)", "(per meeting notes)"

## Step 3: Write output

Write the brief to `output/project_brief_{timestamp}.md` with a metadata header. Present the brief to the user.
