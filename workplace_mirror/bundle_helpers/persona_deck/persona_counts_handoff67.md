# Handoff 67: `persona_counts_results.md` (persona counts, cc_60_180 and rl_60_180, August 2026), lines 1-89

## Context for Claude Code

- Source: 2 phone photos of VS Code (LG monitor), file `tmp_validation/persona_deck/persona_counts_results.md`. Other open tabs: `pipeline_registry.py`, `21_a1_evidence_family_rule.md`, `oos_results.md`. The tab for this file has no `M` or `U` marker. Blame text on line 1 reads "You, 57 seconds ago • Persona counts: results summary (cc_60_180, rl_…" (editor ghost text, not file content; the header line shows "You, 2 seconds ago | 1 author (You)").
- Content: how many personas occur in August 2026 for cards and loans (state and family level), the in-house tier by persona, the top-10 in-house family-level personas for each product, and caveats. Tiers and rates come from the same May back-test and the in-house cut-offs of handoff 61 (cards ≥ 1,250, loans ≥ 6,000).
- Photos merged by editor line number: photo 2 = lines 1-58, photo 1 = lines 34-89. Lines 1-89 are covered. Line 89 is the last line I can see and is empty.
- Format: `NNN  text`, NNN is the editor line number. The file is hard-wrapped, so each editor line is one row. Continuation lines of a numbered item are indented 3 spaces.

## Transcription

```
  1  # Persona counts — cc_60_180 and rl_60_180, August 2026
  2  
  3  Accounts at persona month 2026-08-31: cards 19,292 (19,232 with a known deterioration state, 60 `unknown`),
  4  loans 3,985 (all known). Personas from the August accounts. Tiers and the paid / collected rates from the May 2026
  5  back-test (collections June-August). In-house cut-offs: cards ≥ 1,250, loans ≥ 6,000 AED collected per account.
  6  Possible personas: 648 at state level (6 deterioration states × 9 locatability cells × 3 credibility bands ×
  7  4 ability bands), 432 at family level (4 families in place of the 6 states). Every level was present as
  8  specified, so the product of levels present equals the possible count in both models.
  9  
 10  ## A. How many personas occur
 11  
 12  | Metric | Cards, state | Cards, family | Loans, state | Loans, family |
 13  |---|---|---|---|---|
 14  | Possible | 648 | 432 | 648 | 432 |
 15  | Occurring (at least 1 account) | 393 | 272 | 323 | 221 |
 16  | With 10+ accounts | 222 | 158 | 111 | 88 |
 17  | Personas under 10 accounts | 171 | 114 | 212 | 133 |
 18  | Accounts in personas under 10 | 639 | 419 | 736 | 478 |
 19  | Share of accounts in personas under 10 | 3.3% | 2.2% | 18.5% | 12.0% |
 20  | Median accounts per occurring persona | 13 | 14 | 5 | 6 |
 21  
 22  Cards `unknown` deterioration state: 60 accounts in 26 state-level personas, left out of the counts above.
 23  
 24  ## B. The in-house tier
 25  
 26  | Metric | Cards | Loans |
 27  |---|---|---|
 28  | In-house accounts (share of all August accounts) | 2,077 (10.8%) | 317 (8.0%) |
 29  | Family-level personas in the in-house tier | 51 | 16 |
 30  | Top personas to cover 50% / 80% / 90% of in-house accounts | 12 / 26 / 34 | 6 / 11 / 13 |
 31  | Distinct state-level personas within in-house | 72 | 27 |
 32  | of which under 10 accounts | 17 | 12 |
 33  | State-level personas to cover 50% / 80% / 90% | 15 / 35 / 47 | 8 / 16 / 20 |
 34  | Top 10 family-level personas' share of in-house accounts | 46.8% | 79.2% |
 35  | Tier mix, % of accounts: in-house / agency | 10.8 / 54.1 | 8.0 / 53.9 |
 36  | Tier mix, % of accounts: non-workable / unassigned | 32.4 / 2.7 | 19.8 / 18.4 |
 37  
 38  Family-level personas that got a tier (10+ back-test accounts): cards 159 of 272 occurring, loans 77 of 221.
 39  
 40  ### Top 10 in-house family-level personas — cards
 41  
 42  Paid % and collected per account are the May back-test rates (AED collected June-August).
 43  Columns: Accts = August accounts; In-house % = share of in-house accounts; BT accts = back-test accounts;
 44  AED/acct = AED collected per account.
 45  
 46  | # | Deterioration | Location, reach | Credibility | Ability | Accts | In-house % | BT accts | Paid % | AED/acct |
 47  |---|---|---|---|---|---|---|---|---|---|
 48  | 1 | Stopped paying suddenly | In country, reachable | Low | Unknown | 167 | 8.0% | 155 | 30.3 | 1,274 |
 49  | 2 | Has cured before | In country, reachable | Low | Low | 132 | 6.4% | 159 | 34.6 | 1,350 |
 50  | 3 | Curing now | Unknown, reachable | Moderate | Unknown | 103 | 5.0% | 129 | 69.0 | 1,713 |
 51  | 4 | Stopped paying suddenly | In country, reachable | Moderate | Low | 102 | 4.9% | 91 | 41.8 | 1,962 |
 52  | 5 | Has cured before | In country, reachable | Moderate | Low | 97 | 4.7% | 96 | 42.7 | 1,663 |
 53  | 6 | Has cured before | Skip, reachable | Low | Unknown | 94 | 4.5% | 84 | 23.8 | 1,290 |
 54  | 7 | Curing now | In country, reachable | Moderate | Low | 86 | 4.1% | 83 | 72.3 | 2,603 |
 55  | 8 | Curing now | In country, reachable | Moderate | Moderate | 69 | 3.3% | 106 | 65.1 | 1,794 |
 56  | 9 | Stopped paying suddenly | In country, reachable | Moderate | Unknown | 63 | 3.0% | 59 | 37.3 | 2,373 |
 57  | 10 | Curing now | Unknown, reachable | Moderate | Moderate | 58 | 2.8% | 60 | 60.0 | 1,892 |
 58  
 59  ### Top 10 in-house family-level personas — loans
 60  
 61  | # | Deterioration | Location, reach | Credibility | Ability | Accts | In-house % | BT accts | Paid % | AED/acct |
 62  |---|---|---|---|---|---|---|---|---|---|
 63  | 1 | Has cured before | Skip, reachable | Low | Low | 34 | 10.7% | 26 | 42.3 | 8,290 |
 64  | 2 | Has cured before | Unknown, reachable | Moderate | Unknown | 34 | 10.7% | 32 | 75.0 | 6,677 |
 65  | 3 | Curing now | In country, reachable | Moderate | Low | 33 | 10.4% | 21 | 71.4 | 8,891 |
 66  | 4 | Has cured before | Unknown, non-reachable | Moderate | Low | 27 | 8.5% | 32 | 71.9 | 8,291 |
 67  | 5 | Has cured before | Skip, reachable | Moderate | Low | 23 | 7.3% | 25 | 52.0 | 8,415 |
 68  | 6 | Curing now | In country, non-reachable | Moderate | Low | 23 | 7.3% | 18 | 77.8 | 9,107 |
 69  | 7 | Has cured before | Unknown, unknown | Moderate | Unknown | 21 | 6.6% | 15 | 66.7 | 9,358 |
 70  | 8 | Stopped paying suddenly | Unknown, non-reachable | Moderate | Low | 21 | 6.6% | 27 | 66.7 | 6,761 |
 71  | 9 | Has cured before | In country, reachable | Low | Unknown | 18 | 5.7% | 18 | 50.0 | 11,011 |
 72  | 10 | Has cured before | In country, reachable | Moderate | Moderate | 17 | 5.4% | 13 | 46.2 | 11,323 |
 73  
 74  Deterioration wording: "Curing now" = stabilized; "Has cured before" = slow roller or repeat delinquent;
 75  "Stopped paying suddenly" = seasoned or early-life straight roller (family level, so the two are not split).
 76  
 77  ## Caveats
 78  
 79  1. **Loans are thin.** The median loan persona has 5-6 accounts, 12-18.5% of loan accounts sit in personas under 10, and
 80     the top-10 loan lists rest on 13-32 back-test accounts each, so their paid % and collected figures are noisy.
 81  2. **The tiers are in-sample.** Each tier is cut from the same May back-test collections it is read against. Several
 82     cards personas sit close to the 1,250 cut (rank 1 at 1,274, rank 6 at 1,290, rank 2 at 1,350), so the in-house list
 83     could change if the cut or the back-test month moved. Loans: 18.4% of accounts have no tier because their persona had
 84     under 10 back-test accounts, which can understate the in-house share.
 85  3. **Concentration differs by product.** Cards in-house spreads over many personas (34 for 90% of accounts, top 10 only
 86     46.8%); loans in-house is a short list (13 personas for 90%, top 10 = 79.2%), though on far fewer accounts (317).
 87     Reading deterioration at state level raises the personas needed for 90% of in-house accounts from 34 to 47 (cards)
 88     and from 13 to 20 (loans).
 89  
```

## Notes on specific spots

Checks done on the transcribed numbers:
- Possible personas: 6 × 9 × 3 × 4 = 648 (state), 4 × 9 × 3 × 4 = 432 (family).
- Table A: occurring = with 10+ + under 10 in every column (222 + 171 = 393, 158 + 114 = 272, 111 + 212 = 323, 88 + 133 = 221). Share under 10: 639 / 19,232 = 3.3%, 419 / 19,232 = 2.2%, 736 / 3,985 = 18.5%, 478 / 3,985 = 12.0%.
- In-house accounts: 2,077 / 19,292 = 10.8%, 317 / 3,985 = 8.0%. The tier mix on lines 35-36 matches handoff 61 (10.8 / 54.1 / 32.4 / 2.7 for cards, 8.0 / 53.9 / 19.8 / 18.4 for loans), and so do the 159 and 77 tiered family-level combinations (line 38).
- Top-10 cards: accounts sum to 971, which is 46.7% of 2,077, matching 46.8% on line 34 within rounding. Each "In-house %" equals Accts / 2,077. Each Paid % is consistent with a whole-number count over BT accts (30.3 = 47/155, 34.6 = 55/159, 69.0 = 89/129, 41.8 = 38/91, 42.7 = 41/96, 23.8 = 20/84, 72.3 = 60/83, 65.1 = 69/106, 37.3 = 22/59, 60.0 = 36/60).
- Top-10 loans: accounts sum to 251, which is 79.2% of 317, matching line 34. Each Paid % is a whole count over BT accts (42.3 = 11/26, 75.0 = 24/32, 71.4 = 15/21, 71.9 = 23/32, 52.0 = 13/25, 77.8 = 14/18, 66.7 = 10/15 and 18/27, 50.0 = 9/18, 46.2 = 6/13). BT accts range 13-32, matching line 80.
- Caveat on line 82: the card ranks 1, 6 and 2 at 1,274, 1,290 and 1,350 match the AED/acct column (lines 48, 53, 49).
- Lines 34-58 appear in both photos and matched.

Flagged spots:
- Line 1 uses an em dash "—" (as in the breadcrumb); the editor showed it as a long dash. The H3 headings on lines 40 and 59 also use "—".
- Line 46 and 61: the divider line (47, 62) has 10 groups, matching the 10 header columns.
- Line 29 ("Family-level personas in the in-house tier": 51 / 16) was legible. Line 31's 72 / 27 and line 32's 17 / 12 were also legible, but are not checkable from other numbers in the file.
- Line 89 is empty and is the last line visible. I can't tell whether the file continues.
