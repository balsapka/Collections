# Handoff 62: terminal log, Claude Code answer on agency commission vs outright sale

## Context for Claude Code

- Source: 1 phone photo of the VS Code window in the dev container `retail.collections.risk_profiling` (branch `feature/persona_refactor`, `modified:2 untracked:1 stash:1`). Not a file. It is the terminal pane with a Claude Code answer, plus the editor tabs above it.
- The question (top of the terminal) is cut off at the right edge of the screen, so the last words are missing (see notes).
- The answer is copied as printed. The terminal wraps long lines, so I joined each wrapped bullet back into one line. Indentation of the sub-bullets is as shown (2 spaces for the `-` bullets).
- The Mac link was not available for this batch, so this file is delivered through the chat and not written to `~/Python/Collections/pics/`. Copy it there if you want it with the others.

## Editor area (above the terminal)

- Open tabs, left to right: `...eline_registry.py` (cut off at the left, presumably `pipeline_registry.py`), `fill_in.md`, `fill_in_changes.md` (marked `U`), `Emirates NBD Services - FR Policy on Operations - Jul2025.pdf`, `Extension of PLUS and CARES 2026.docx` (active, with a close X).
- Breadcrumb (cut off at the left): `input > docs > Extension of PLUS and CARES 2026.docx`
- Editor message: "The file is not displayed in the text editor because it is either binary or uses an unsupported text encoding." with a blue button "Open Anyway".

## Terminal

Panel tabs: PROBLEMS (cut off), OUTPUT, DEBUG CONSOLE, TERMINAL (active), PORTS.

```
> I'm trying to answer this question. Based on all your use case knowledge and memory, and @data/input/docs files, can you answer this: do we route delinquent accounts to agencies on commission or we outright sell them (write…
  Searched for 1 pattern, read 1 file, ran 7 shell commands

──────────────────────────────── 1 new message ────────────────────────────────

● Agencies on commission is confirmed. An outright sale is not documented. Write-off is an accounting step, not a separate route. Write-off and agency collection are not mutually exclusive.

  What the docs say
  - Agencies are paid commission on cash collected. The FR Policy on Operations (Jul 2025, "Commission Payout") says accounts are referred to third-party agencies by product, DPD stage, contactability, charge-off vintage (for 180+) and strategy. Agencies are paid only on cash collection.
  - Commission varies by DPD stage and charge-off vintage. There is a rate card for agencies handling consecutive buckets. There are separate commissions for skip-tracing data enrichment and for car repossession. FR proposes the structures, and Group Retail Risk and the GCRO approve them.
  - Agency routing starts at 180+. The policy says 180+ accounts go to the in-house recoveries team or to agencies, depending on how hard they are to collect and whether the customer can be contacted. Allocation can also send non-workable, non-contactable, least-likely-to-pay accounts to external agencies.
  - Agency allocation is also allowed earlier. The Appointment of Third-Party Agency Letter triggers for any delinquent account up to 180+ DPD allocated to an agency with a positive balance.
  - Write-off is a bookkeeping step. The Settlement Desk "writes off the liabilities for honored settlements." The PLUS/CARES extension doc covers settlements for 180+ DPD and charge-off vintages, with 2025 recoveries of AED 257M against a plan of AED 218M.
  - A written-off account is still collected. Our own Way4 findings (CC_DATA_FINDINGS.md) show write-off accounts keep non-zero balances, so recovery effort continues after charge-off.
  - I found no sale of delinquent accounts to a third-party buyer. Searching the policy for "debt sale", "buyer" and "portfolio sale" returned nothing, and the PLUS/CARES doc has none either. The only "sale" references are property auction on repossession and "sales purpose" feedback requests.

  What this means for our work
  - The "sell" in our 180+ keep/sell cutoff (domain_and_decisions.md, S4) is our own working shorthand. The policy doesn't confirm it. In the policy, the alternative to in-house is an agency on commission.
  - Open question 01 asks for agency commission or sale price by cohort, and it is still unanswered. I'd ask the business whether any debt sales happen in practice. If none do, the cutoff should be priced as in-house cost against agency commission, plus settlement terms.

  Caveats
```

Below the "Caveats" heading the screen shows only a horizontal rule and the input prompt `›` (empty, with a cursor). Bottom right of the terminal: "✓ Update installed · Restart to apply" (green).

Status lines under the prompt:

```
 ◆ Sonnet | mode: auto | ● 4% | feature/persona_refactor modified:2 untracked:1 stash:1 | retail.collections.risk_profiling | tkn: 67.1K in: 136 op: 66.9K
 Today Overall Usage burn: 0.0% tkn: 68.3K in: 138 op: 68.2K
 ▶▶ auto mode on (shift+tab to cycle)
```

## Notes on specific spots

- The question is truncated at "(write…". The next words are probably "(write-off?)" or similar. I can't tell, so I didn't guess.
- The "Caveats" heading is the last line of the answer on screen, with no text under it. Either the answer ends there, or the caveats hadn't been printed yet or were scrolled out of view. Check the terminal if you need them.
- Figures: AED 257M (2025 recoveries) against a plan of AED 218M. Both read clearly.
- Names to check against the repo: `CC_DATA_FINDINGS.md`, `domain_and_decisions.md` (S4), "Open question 01". The two documents quoted are "FR Policy on Operations - Jul2025" and "Extension of PLUS and CARES 2026".
- "GCRO" and "FR" are as printed. "Way4" is the card system name as printed.
- The PDF tab name reads "Emirates NBD Services - FR Policy on Operations - Jul2025.pdf". The Word file's name reads "Extension of PLUS and CARES 2026.docx".
- The status lines show 4% context used, 67.1K tokens in the current session (136 in / 66.9K out) and 68.3K tokens for today (138 in / 68.2K out). The "◆", "●" and "▶▶" glyphs are my reading of small icons.
