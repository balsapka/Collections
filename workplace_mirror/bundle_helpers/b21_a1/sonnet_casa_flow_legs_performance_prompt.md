# A1 bundle 21: `prm_casa_flow_legs` stalls — make the legs node cheaper (UAT, no data)

## Goal

After the split (previous prompt), the five older `casa_features` nodes finish in about 25 minutes,
but `build_casa_flow_legs` → `prm_casa_flow_legs` stalls, as the single flows node did before.
The user has no Spark UI. Make the node cheaper **without changing its output** (same rows, same
`flow_class` per leg).

## What the node does today

Scans `prm_casa_transactions` (all customers, 12 months before the persona start + persona months),
keeps CASA accounts, aggregates **all** of `wm_pri_labelled_transactions` per
`(cif_id, tran_id, tran_date[, in_out_flow])`, left-joins it, then adds lane and flow class.
`wm_pri_labelled_transactions` is WM's 03_primary table: not a snapshot (`globals_dev.yml`), filtered
only by `to_date(tran_date) >= floor` in our code.

## Decisions (Claude Code)

1. **Keep only label rows that carry a label we use, before the aggregate.** A label row with every
   flag we read at 0 / NULL (`salary_txn_flag`, `self_transfer_flag`, and the flags you added for
   `fees_charges` and the loan payment) changes nothing: after the left join it becomes `false`
   anyway. Filter to rows where at least one of them is set, then aggregate. Expect this side to
   shrink to a small share of the table. If it is then small enough by your judgement of the table,
   broadcast it; otherwise leave the join to Spark.
2. **Prune partitions and columns on the WM side.** The PROD Spark UI shows the read lists **all 280
   weekly partitions** of `.../wealth_management/03_primary/pri_labelled_transactions_indicators_by_week/
   week_number=…` (about five years), so nothing is pruned today. Add a filter on `week_number`
   (`yyyyMM0W`: compare it with the floor month as `yyyyMM01`, or whatever form the column has; check
   its type) so Spark reads only the weeks from the floor month on; keep the `tran_date` filter for
   exactness. Select only the key and flag columns before anything
   else.
3. **Legs without a usable key skip the join.** Legs whose `cif_id` or `tran_id` is NULL or blank
   can never match a label, but in a left join they all hash to one partition (one task that never
   finishes). Split them off, give them `wm_salary = wm_self = … = false`, and union them back
   after the join.
5. **Few files per output partition.** In PROD all Spark jobs finished and the app sat idle, still
   running: the driver is committing the partitioned overwrite (renaming each task's file into every
   `event_month` folder on HDFS). Repartition by `event_month` right before the save
   (`df.repartition("event_month")` in the node's return) so each month folder gets one file instead
   of one per shuffle partition. Do the same for any other partitioned output this bundle added.
4. **Prune transaction columns early.** Right after the read, select only the columns that
   `transaction_lane`, `flow_class` and the output need.

## Hard rules

- No change to class rules, the date floor, the output columns or the output rows of
  `prm_casa_flow_legs` / `feat_cif_casa_flows_monthly`.
- Kedro I/O through node inputs/outputs only; `model_id` from globals; no `kedro run` in UAT; no
  global Spark config change (report the current `spark.sql.adaptive.*` settings instead).
- Touch only `feat_cif_casa.py`, `pipelines/casa/features.py` (if a new input is needed) and the
  tests.

## Deliverables

1. The five changes; tests updated and passing, plus one test that a leg with a blank `tran_id`
   keeps its class and one that a label row with every flag 0 changes nothing; black / pylint
   clean.
2. Report: the partition column of `wm_pri_labelled_transactions` (or "none"), the current
   `spark.sql.adaptive.enabled` / `skewJoin.enabled` values, and whether you broadcast the labels.
3. The PROD command for the legs node alone, then the flows node.
4. A short "Performance fix 2" section appended to `data/input/a1_bundle21_apply_summary.md`.
