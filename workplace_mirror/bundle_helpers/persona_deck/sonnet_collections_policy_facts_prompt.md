# Collections policy facts for the allocation tiers

## Goal

We are proposing an allocation view for delinquent accounts at 61–180 DPD with three groups:
- accounts worth working in-house;
- accounts to place with an external agency;
- accounts where almost nothing is expected back: the bottom third of card accounts recover under 0.5% of outstanding principal in 3 months, yet still get about 11 in-house call days per 3 months.

Before we name and present these groups, we need the facts on how the bank actually allocates, places and pays for collections, **taken only from the documents**. Nothing may be inferred or filled in from general industry knowledge.

## Sources

Every document under `data/input/docs/`, including at least:
- `Emirates NBD Services - FR Policy on Operations - Jul2025.pdf`
- `Extension of PLUS and CARES 2026.docx`

If a document can't be read (binary or encoding issues), convert it with whatever tool is available (for example `pdftotext`, `python-docx`) and say which documents you could not read.

## Questions

Answer each one. **Run subagents in parallel**, one per group (A–E). Each subagent searches every document for its group.

**A. Allocation at 61–180 DPD**
1. How are accounts at 61–180 DPD allocated today: in-house teams, agencies, or both? What criteria decide it (product, DPD stage, balance, contactability, scores, strategy)?
2. Can accounts below 180 DPD be placed with agencies? Under what conditions, who approves it, and is there a minimum DPD or a balance limit?
3. Is there any concept of "non-workable", "non-contactable" or "least likely to pay" accounts? How is it defined, and what happens to them?
4. Is there any rule for reducing or stopping collection effort on an account before 180+ (for example letters / SMS only, no calls)?

**B. Agency economics**
5. How are agencies paid (commission on cash collected, fixed fees, both)? Give the rate card by DPD stage, charge-off vintage and product, with the figures exactly as written.
6. Are there different placement types or terms (for example priority vs bulk, primary / secondary / tertiary placement, consecutive buckets, recall rules, placement duration)?
7. Are there agency performance targets, minimum effort requirements or recall rules if an agency does not work an account?
8. Is there any figure for the cost of in-house collection (per account, per collector, per call)?

**C. Sale and write-off**
9. Is any sale of delinquent or charged-off debt to a third party mentioned anywhere? (Search: sale, sell, buyer, portfolio sale, debt sale, assignment, transfer of receivables.)
10. When is an account charged off or written off (DPD, product), and does collection continue after it? Who collects after write-off?

**D. Conduct and customer rules**
11. Are there rules on contact frequency, channels or timing that apply to in-house teams or agencies (for example a maximum number of calls)?
12. Are there restrictions on using agencies for accounts that are not charged off (customer experience, branding, complaints, regulator)?

**E. Settlements and programmes**
13. What do PLUS and CARES offer, to which DPD stages and vintages, and with what results (state the figures exactly as written)?
14. Are any other settlement, restructuring or hardship programmes available at 61–180 DPD?

## Rules

- **Evidence only.** Every answer cites the document, the section heading and the page (or paragraph), with a short quote of at most two lines.
- If a document doesn't answer a question, write **"not found in the documents"**. Don't answer from general knowledge, and don't guess.
- Keep figures exactly as written (currency, %, units).
- Mark anything that looks outdated, for example a superseded date or a draft.
- Read only: no code, no data, no pipeline changes.

## Deliverable

Write `tmp_validation/persona_deck/collections_policy_facts.md` with three parts:
1. The 14 answers, grouped A–E, each with its citations.
2. A **"What this means for the three groups"** section of at most 6 lines, stating only what the documents support:
   - Can the low-yield group be placed with agencies before 180+?
   - On what commission terms?
   - What stops it, if anything?
3. A list of documents that could not be read.

Commit and push, then paste the whole file back.
