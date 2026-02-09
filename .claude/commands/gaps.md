---
description: Find contradictions, gaps, and cross-document issues across all processed outputs
allowed-tools: Bash, Read, Glob, Grep, Write
---

Perform a cross-document gap and contradiction analysis across all agent outputs.

## Step 1: Read all outputs

Read every markdown file in `output/` (excluding previous `gap_analysis_*.md` files).

## Step 2: Analyze for issues

Look for these categories of problems:

### Contradictions
Rules, thresholds, or statements in one document that conflict with another. For example:
- Policy says write-off at 180 DPD, but email from CFO mentions 270 DPD
- Policy prescribes action X for a bucket, but meeting notes say "we never actually do X"
- Data profile shows a field exists, but stakeholder says "we don't track that"

### Data Gaps
Cross-reference what the policy analysis says is needed for modeling against what the data profiles show is available. Flag:
- Features recommended by policy analysis that don't exist in any profiled dataset
- DPD buckets mentioned in policy but not represented in data
- Outcome labels needed for the target variable that aren't captured

### Unanswered Questions
Questions raised in one output that another output might answer (or explicitly doesn't):
- Stakeholder questions from policy Pass 3 that email threads or meeting notes address
- Data gaps flagged in profiles that meeting notes mention being "in progress"

### Coverage Gaps
- Products mentioned in policy (credit cards, personal loans, Murabaha, etc.) that no data file covers
- DPD ranges in policy that have no data representation
- Stakeholders mentioned but never heard from

## Step 3: Prioritize

Rank all findings:
- **CRITICAL**: Blocks modeling entirely (missing target variable, fundamental data gap)
- **HIGH**: Will significantly impact model quality or scope
- **MEDIUM**: Needs clarification but has workarounds
- **LOW**: Nice to resolve but not blocking

## Step 4: Write output

Write findings to `output/gap_analysis_{timestamp}.md` with metadata header. Present the prioritized findings to the user.
