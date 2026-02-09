---
description: Clean up and format a raw, messy notes file (fix whitespace, structure, readability)
argument-hint: file-path
allowed-tools: Read, Write
---

Clean up and format the raw notes file at `$ARGUMENTS`.

## What to do

Read the file. It's a raw paste of someone's notes — expect:
- Excessive blank lines and trailing whitespace
- Inconsistent indentation
- No markdown structure (or broken markdown)
- Run-on text with no paragraph breaks where there should be
- Random bullet styles (*, -, •, >) mixed together
- Orphaned lines that belong to the previous point

## Formatting rules

1. **Remove excessive whitespace** — collapse 3+ consecutive blank lines down to 1. Trim trailing spaces on every line.
2. **Normalize bullets** — pick `-` as the standard bullet. Convert `*`, `•`, `>` used as bullets to `-`. Keep nested indentation with 2 spaces per level.
3. **Add paragraph breaks** where a clear topic shift happens (but don't over-split — keep related thoughts together).
4. **Do NOT change the content** — no rewording, no summarizing, no adding your own text. This is purely structural cleanup.
5. **Do NOT add markdown headers** unless the original text clearly had section titles (e.g., an all-caps line or a line ending with `:`). In that case, convert to `## Header`.
6. **Fix obvious line-break damage** — if a sentence is split mid-word or mid-phrase across lines (common from copy-paste), rejoin it.
7. **Preserve exact names, numbers, and domain terms** — never alter these.

## Output

Overwrite the original file with the cleaned version. Show the user a brief before/after comparison (first ~10 lines of each) so they can verify.
