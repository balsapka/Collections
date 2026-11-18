# a1_card_parent summary (cc_60_180, Q-S6-14)

Source: `results_cc_60_180.md` (PROD). Scored month = latest persona month 2026-08-31 (19,292
accounts); `prm_card_month_end` runs to 2026-10-31.

## Verdict: neither H1 nor H2 as stated, and it barely touches F4

`parent_contract_idt` is rare (1.3% of 4.52M card contracts have a parent, 0.5% are named as one)
and is a **link between contracts that stay live side by side**, not a clean replacement and not an
account -> card hierarchy.

Numbers that decide it:
- **Not H1 (replacement):** only 13.3% of parents are closed, and <10 pairs have a parent closed on
  or before the child's open date. Of pairs with month-end rows on both sides, 100% overlap (median
  21 months, i.e. the whole window); sequential pairs <10. The parent is older in 84% of pairs (64%
  by more than a year), but it does not leave.
- **Not H2 (account -> card layers):** 67% of parents have one child, 16.6% two, 10% four or more. A
  hierarchy would mostly show several children per parent. Status pairs run both ways (Normal parent
  / Active child 19%, Active parent / Normal child 18%), so there is no fixed account-level role.
- **A corporate link exists:** 61% of pairs cross CIFs (parent in another CIF than the child) and
  60% are parent `client_category` C with child P. Only 39% are same-CIF pairs, the only kind that
  matters for F4. Different-CIF pairs cannot affect a scored account's own CIF.
- Status mix: 18% of pairs are an active parent with a declined/pick-up child, 14% the reverse, so
  the pair often has one live and one blocked contract. Open dates are the same day in 16%.

## Effect on F4 (scored accounts, 2026-08-31)
- Scored account named as a parent (dropped by `_cards`): 19 (0.1%). The same 19 have a child, and
  F4 counts their own children as "another card" (0.1%); for 18 of them those children are the only
  card rows F4 sees.
- F4 misses the CIF's other accounts: other scored account dropped as a parent <10 (of 1,097
  accounts in 536 multi-account CIFs); CIFs with another card but none left after the drop <10.
- Only 11.8% of scored accounts have another card contract at all, so the card branch is thin
  whatever the parent rule does.
- Month-end rows dropped as parents: 0.6% in the latest month (13,801 of 2.2M), 0.5% over all
  months.

## Gaps
- "Has a parent" and several B5 and B2 cells are `<10` (suppressed); "has at least one child" equals
  "named as a parent" by construction.
- 70,433 contracts (1.6%) carry more than one CIF in `prm_card_contracts` (client table gives
  several `ident_number` per `client_idt`); this inflates pair and row counts slightly (58,852 pairs
  vs 57,455 in B3) and is not part of this question.
- Only 73% of children have a month-end row (billing window); first-month equality (91%) is the
  window start, not evidence.
- `product_id` (161 values) and `int_product_add_info` (1,363) not crosstabbed (too many values); no
  contract-type or level column exists on the contract table, so contract level cannot be read from
  it.
- The scored month (08-31) is earlier than the latest month-end row (10-31); B3/B4 use the latter,
  B5 the former.

## Proposal
No change needed for the retail CC persona: the parent rule affects 0.1% of scored accounts. If the
19 are to be cleaned up, one line: in the F4 card branch exclude contracts whose
`parent_contract_idt` is the scored account (own children), and keep dropping only same-CIF parents;
do not treat different-CIF links as replacements. Not coded.
