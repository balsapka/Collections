# A1: why does a card contract carry more than one CIF? (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. Run for `cc_60_180`, then paste `summary_cc_60_180.md` back here. Why:
the card parent-link check found 70,433 card contracts (1.6%) under more than one `cif_id` in
`prm_card_contracts`, because `raw_stg_client` gives several `ident_number` per `client_idt`.
`build_card_contracts` joins contract → client over the whole tables with no date, so a CIF that changed over
time (or a contract that moved to another client) leaves the contract under every CIF it ever had. F4 then
counts the card for each of them. The fix goes into the next A1 bundle, so the numbers below must pick the rule.

````text
Goal
Find why a Way4 card contract maps to more than one CIF in prm_card_contracts, and which CIF rule the
product primary should use. Aggregates only; change no pipeline code.

Context (read the code first)
- nodes/primary/products/prm_products.py build_card_contracts: cif = raw_stg_client (client_idt,
  ident_number as cif_id) distinct; contract (contract_idt, client_idt, parent_contract_idt) joined to it on
  client_idt; no date filter on either table, distinct rows.
- nodes/features/products/feat_cif_cross_product.py _cards: every card row of prm_card_month_end joined to
  prm_card_contracts on contract_id takes that row's cif_id, so a contract under two CIFs is a card of both.
- The persona's own CIF for a card is cc_spine.cif_id per (contract_id, observation_date); the CC obs base
  takes the largest cif_id when the spine disagrees within a month (_common.build_cc_obs_base).

Hypotheses
- H1 CIF changed over time: raw_stg_client keeps history (load-date partitions or amendment rows) and a
  client_idt's ident_number changed; the old and new values never coexist on one load date.
- H2 several CIFs at once: on the same load date one client_idt has more than one ident_number (another
  identity type held in ident_number, joint or corporate clients, data error).
- H3 contract moved client: raw_stg_contract keeps history and a contract_idt's client_idt changed.
Say which hold and in what share of the 70k contracts.

Rules (hard)
- catalog.load only, no spark.read or paths. model_id = catalog.load("params:model_id"), in every output file
  name; run for cc_60_180.
- Aggregates only: counts and shares, no ids, no customer rows; cells under 10 as "<10".
- Temporary tracked folder tmp_validation/a1_card_cif/ (Kedro-notebook snippet + README); commit and push.
  The user runs it in PROD, commits results_<model_id>.md; back in UAT you write the summary. No pipeline,
  catalog or registry change.
- Literal date filters right after catalog.load; one pass per table group; broadcast small tables; no
  row-level collect.

Aggregates to save (design the exact tables; they must decide between H1-H3 and the rule)
1. Columns: the column names of raw_stg_client and raw_stg_contract with their types, the partition
   column(s), and distinct-value counts for any date, amendment, status or identity-type column (for
   example edp_load_date, amnd_date, amnd_state, date_open, client_type, id type). Say how many load dates
   each table holds and whether each load date is a full snapshot or only changes.
2. Client side: client_idt with more than one ident_number over the whole table (count, share); of those,
   the share whose values never share a load date (H1) vs share at least one (H2); for H1, how many changes
   per client (1, 2, 3+), the months the changes happen (by year), and whether the old value ever returns.
   Describe ident_number for single- vs multi-CIF clients: length and digit-only patterns, share
   that also appear as cc_spine.cif_id.
3. Contract side: contract_idt with more than one client_idt over the whole table, same split by load date
   (H3), and how many of the 70k multi-CIF contracts this explains.
4. Against the spine: for (contract_id, month_end) in cc_spine (persona months), the share where cc_spine's
   cif_id equals (a) the CIF from the latest client and contract rows on or before that month end
   (point-in-time), (b) the latest CIF of all (today's), (c) any of the CIFs in prm_card_contracts; and
   the share of cc_spine contract-months with more than one cif_id itself.
5. Effect on F4 at the latest persona month: scored accounts (cc obs base) whose contract sits under more
   than one CIF; card rows of feat_cif_cross_product_monthly that sit under a CIF other than the
   point-in-time one; scored accounts whose xp_current / xp_instalment_max use such a card (count, share);
   and the same with the rule "cc_spine's cif_id for that contract-month" where the spine has the contract.

Summary (write summary_<model_id>.md, at most one page)
- Verdict: H1 / H2 / H3 with shares and the two or three numbers that decide it.
- The rule you recommend for prm_card_contracts (point-in-time CIF per month end, the latest CIF, or the
  spine's CIF where it exists), with its agreement with cc_spine and the F4 effect from 5. Do not code it.
- Gaps: missing columns, suppressed cells.
````
