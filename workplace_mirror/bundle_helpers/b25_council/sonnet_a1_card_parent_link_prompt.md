# A1: what does `parent_contract_idt` link? (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet (Q-S6-14, council run 2, user 2026-11-15). Run for `cc_60_180`, then
paste the summary back here. Why: F4's card branch drops every contract named as a parent as "replaced by a
newer one". If Way4 uses the field for the card -> account hierarchy instead, account-level contracts with
cards are dropped, card-level contracts stay, and F4 may count the scored account's own cards as "another
card" or miss the customer's other accounts.

````text
Goal
Decide what `parent_contract_idt` means in Way4, from aggregates, before GRR reads the F4 card results.
Change no pipeline code.

Context (code, read it first)
- `nodes/primary/products/prm_products.py` `build_card_contracts`: `prm_card_contracts` = `cif_id`,
  `contract_id`, `parent_contract_id` (from `raw_stg_contract.parent_contract_idt`), one row per card contract
  whose client is known.
- `nodes/features/products/feat_cif_cross_product.py` `_cards`: contracts named as a `parent_contract_id`
  are removed ("replaced"); the rest, joined to `prm_card_month_end` (`contract_id`, `month_end`, `level`,
  `minimum_due`), give the CIF's `card` rows (`xp_current`, `xp_instalment_max` for F4).
- The scored account is `account_id` of the CC obs base (= the card contract the observation is about).

Hypotheses
- H1: `parent_contract_idt` links a replaced (older) contract to its replacement. Then a parent is older than
  its child, usually closed or inactive once the child is live, and the pair shares a CIF. F4 is right.
- H2: it links card-level contracts to their account-level contract (hierarchy). Then a parent is an account
  contract with several children at once, both live in the same months, often an older or same-day open
  date. F4 drops the account contracts and keeps the card-level ones, so it may count the scored
  account's own cards as "another card".
- Mixed: both uses exist; say in which share.

Rules (hard)
- Catalog loads only (`catalog.load`), no `spark.read`, no explicit paths. `model_id` from
  `catalog.load("params:model_id")`, never hardcoded or overridden, and in the output file name. Run for
  cc_60_180.
- Aggregates only: counts and shares, no customer rows, no ids in the output. Suppress cells under 10.
- Work in a temporary tracked folder (e.g. `tmp_validation/a1_card_parent/`) as a Kedro-notebook snippet;
  commit and push it. The user runs it in PROD, saves `results_<model_id>.md` there, commits and pushes. Back
  in UAT, you analyse it and write the summary. No pipeline, catalog or registry changes.
- If a column you need is not on `prm_card_contracts` / `prm_card_month_end` (contract type, level, open date,
  status), take it from the primary or staging table that holds it only in the snippet, name the dataset in
  the README, and say what is missing instead of guessing. List any contract type / level / hierarchy column
  you find on the contract table (names and distinct-value counts only).

Aggregates to save (design the exact tables; they must decide H1 vs H2)
1. Parent share: of `prm_card_contracts` rows, the share whose `parent_contract_id` is not null, and the
   share named as a parent by another row (distinct contracts); number of children per parent (distribution:
   1, 2, 3, 4+).
2. Pairs (child, parent) with both in `prm_card_contracts`: share with the same `cif_id`; share where the
   parent's `contract_id` is missing from the table (parent not a card contract); open-date order (parent
   older / same day / newer), if an open date exists; contract type / level columns of parent vs child, as
   crosstabs, if they exist.
3. Overlap in time: for pairs, the share where both parent and child have a `prm_card_month_end` row in the
   same month (over all months, and in the latest persona month), and the median number of overlapping months.
4. `prm_card_month_end` rows (latest persona month, and all months): share whose contract has a parent; share
   whose contract is itself named as a parent; share of both.
5. Scored accounts (`account_id` of the cc obs base, latest persona month): share that are named as a parent
   (so `_cards` drops them); share that have a parent; share that have at least one child; share of scored
   accounts for which F4's card branch counts at least one card of the same CIF that is a child of the scored
   account (the scored account's own cards counted as "another card"); share for which `_cards` returns at
   least one card row of the same CIF; and, among CIFs with two or more scored accounts, how many of the
   other accounts are dropped as parents.

Summary (write `summary_<model_id>.md`, at most one page)
- Verdict: H1, H2 or mixed (with the share of each), and the two or three numbers that decide it.
- Whether F4 counts the scored account's own cards (share of scored accounts), and whether it misses the
  CIF's other accounts (share).
- Gaps: any column you could not read, any cell suppressed.
- If H2 holds in a material share, a one-line proposal for the rule (e.g. exclude children of the scored
  account's contract; treat only same-CIF, older-and-inactive parents as replaced), without coding it.
````
