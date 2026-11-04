# A3: V1d, where are the payments DCORE calls paid? (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet in the same `tmp_validation/a3_v1_v4/` work. Run in PROD for
cc_60_180 and rl_60_180, then paste `summary_v1d.md` back here.

Why: V1c (`v1c_summary_60_180.md`) found that card payments cover only 22% of CC settlement instalments
DCORE marks paid (35% with 5 days' grace), and 52% / 69% of PTP. RL settlement is backed 53%. The user
asked for a proper investigation before D-A3-11 (DCORE status vs ledger) is decided. The key question is
whether the money reaches the bank in some other way, or whether DCORE marks instalments paid that never
were.

````text
Goal
V1c compared DCORE instalment status with the payment ledger. When DCORE says an instalment is paid,
CC card payments cover it only 22% of the time for settlements and 52% for PTPs (35% / 69% with 5
days). RL settlement 'paid' is backed 53% by int_loan_master.total_paid. Before we decide whether A3
judges kept / broken by DCORE or by payments, find out where that money is, if anywhere. Aggregates
only. Change no pipeline code.

Population
The concluded instalments of V1c (same population, anchor, window, non-cancelled, ledger rule), CC and
RL, PTP and settlement. Put each instalment into one of three groups:
  G1 DCORE paid, ledger not kept at due date + 5 days (RL: within the due month): the gap;
  G2 DCORE paid, ledger kept (control);
  G3 DCORE overdue (control).
Report every result below per group, per plan type (PTP / settlement), per model.

Hypotheses (each one gets a verdict: supported / not supported / partly, with the key numbers)
H1 Card, different form. The money is on the card but not counted as a payment: another txn_category,
   is_post_block_x_fee = 1, a credit adjustment / waiver / reversal, or rows lost in
   crx_cc_transactions (build_cc_transactions ends with .distinct(), which merges identical same-day
   payments, and it drops rows on the way). Compare all credit-side rows of the card in
   [plan start, due date + 30 days] in crx_cc_transactions AND in its upstream source, by category /
   description: count and amount against the instalment's due.
H2 Way4 payment fields. Find the Way4 contract or balance fields that log the last payment (amount,
   date) and any period paid total (the user mentioned a last payment amount / date field). How often
   do they show a payment in [plan start, due date + 5 days] that covers the cumulative due, when the
   transactions don't?
H3 Balance movement. Does the card's outstanding (total due / overdue amounts / statement balance in
   crx_cc_balance or cc_spine) drop by at least the instalment's due amount between the statement
   before the due date and the one after? A drop without a payment row points at a waiver or a
   write-off, not money.
H4 Another account. The customer pays from or into another account: comp_financial_tran_repos_dly
   (FTR) legs of all the CIF's accounts in [plan start, due date + 5 days] whose amount is at least
   the instalment due (or the narration names the card / a card payment / collections / settlement),
   and payments to other cards or loans of the same CIF. Use the FTR row-handling reference
   (docs/context/reference/ftr_transaction_handling.md) to separate real money from bookkeeping rows.
H5 Late. The money comes, but later: days from the due date to when cumulative payments first cover
   the cumulative due (<=5, 6-15, 16-30, 31-60, >60, not by the observation date).
H6 Partial. Something was paid but not enough: share of the cumulative due covered by the cut-off
   (0, under 50%, 50-99%).
H7 DCORE's own reading. What DCORE stores on G1 instalments: paid amount / paid date (null?), when
   the status changed against the due date, plan type or settlement kind (full settlement vs
   instalment plan), later cancellation, any channel / agent / source field. Does DCORE mark a whole
   plan paid at once?

Outcome: does the delinquency behave as if they paid?
For G1 / G2 / G3: the account's delinquency level at the statement (CC) or month-end (RL) before the
due date, and 1 and 2 cycles after: share cured / improved / held / rolled. If G1 behaves like G2, the
money is arriving somewhere; if it behaves like G3, DCORE is wrong.

RL
For RL settlement G1, and for RL PTP 'overdue' instalments the ledger calls kept (24.6% in V1c): use
FTR legs on the loan account itself (day-level dates) to split paid by the due date / paid later in the
month / not paid, and say whether int_loan_master has any other paid or last-payment field that helps.

Rules
catalog.load only (FTR and Way4 tables through their catalog entries); model_id =
catalog.load("params:model_id"), in every output file name; aggregates only, no account / agreement /
CIF ids, cells under 10 as "<10". A part that fails records its error and the rest still runs.

Performance (hard rules: the V1-V4 / V1c snippets ran for hours and section 4 died on a Java heap
error from driver-side plan growth, not data volume)
- Build the instalment list with its group once (~17k CC, ~1.2k RL instalments): only the columns
  needed, then persist + count, or localCheckpoint(), so later parts start from a short lineage. Never
  write row-level data into the tracked folder.
- Read only the partitions needed. From the instalment list, collect two scalars to the driver:
  lo = min(plan start) and hi = max(due date) + 30 days (the widest window any part uses). Filter
  every source with literal values right after catalog.load, before any join or select of the rest:
    - Hive / raw sources (FTR, Way4, the raw source behind crx_cc_transactions, DCORE raw if used) on
      their partition column (edp_load_date for FTR and the Way4 extracts), widened by the same
      EDP_LOAD_DATE_BUFFER_MONTHS buffer as cc_raw_extract/_window_utils.prune_by_edp_load_date;
    - WM / our partitioned outputs on their partition column (week_number, event_month);
    - flat parquet outputs (crx_cc_transactions, crx_cc_balance, cc_spine, int_loan_master, the dcore
      tables) on their date column, so the filter is pushed down.
  A filter written as a join to the instalment list does not prune: use literals.
- Check pruning before the heavy work: for each partitioned source print the physical plan
  (df.explain()) and confirm PartitionFilters is not empty. If it is, fix the filter (column type,
  string vs date) before running that part. Record the filter and the partitions read per source in
  the README.
- Then narrow to the population: inner join to the distinct account / CIF list with
  F.broadcast(...) (a few thousand to ~20k keys), right after the date filter.
- No plan growth: no Python loops that chain window / join steps on one DataFrame. Compute the three
  groups and all buckets in one groupBy with conditional aggregates per part. After each part:
  unpersist what it cached (or spark.catalog.clearCache()).
- No collect() / toPandas() of row-level data; only the final aggregates come to the driver.
- Time a dry run on the latest 3 months of due dates first; if a part takes over ~10 minutes there,
  fix it before the full run. Report each part's runtime in the results file.

Deliverables
1. Snippet + README_v1d.md in tmp_validation/a3_v1_v4/, pushed from UAT. The README names every table
   and column used for H1-H4 and why.
2. The user runs it in PROD for cc_60_180 and rl_60_180 and commits results_v1d_<model_id>.md.
3. Back in UAT: summary_v1d.md, under 60 lines: group sizes; one line per hypothesis per model with
   verdict and key numbers; the delinquency outcome table for G1 / G2 / G3; then one paragraph: what
   share of G1 is explained by H1-H6 combined, and whether DCORE 'paid' or the payments are the better
   judge of a kept instalment.
````
