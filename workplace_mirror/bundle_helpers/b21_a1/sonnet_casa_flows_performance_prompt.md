# A1 bundle 21: `casa_features` times out — fix the flows node (UAT, no data)

## Goal

`kedro run --pipeline=casa_features` no longer finishes in PROD: Spark times out. The five older
nodes are unchanged since they last ran; the new `build_feat_cif_casa_flows_monthly`
(`feat_cif_casa.build_casa_flows`) is the cause. Make it run, with the same result.

## Diagnosis (decided, Claude Code)

1. **`_net_mirrored` is quadratic per customer.** Its join's only equality is `cif_id`; the day
   window, direction and amount are all non-equi conditions, so Spark compares every counted leg
   of a customer with every non-counted leg of that customer over the whole history (12 months
   before the persona start plus the persona months). A customer with tens of thousands of legs
   alone makes hundreds of millions of comparisons, on one task.
2. **The classified legs are computed three times** (the counted side, the mirror side and the
   final anti-join each re-read `prm_casa_transactions`, re-aggregate the WM labels and re-join).

## Decisions

1. **Replace `_net_mirrored` with the equi-join version below.** Each non-counted leg is exploded
   over the 7 days it can mirror (±`NET_DAYS`) with its direction flipped, so the join keys are
   customer, day and direction; only the ±1% amount test stays a condition. Same rule, same
   result: Claude Code ran it through the 92-case A1 spec test (all pass, unchanged). Keep your own
   edits elsewhere in the file (the `in_out_flow` join, the extra WM flags, the wash-lane order).

```python
def _net_mirrored(legs: DataFrame) -> DataFrame:
    """``legs`` without the counted legs (money in / out classes) that an opposite leg of
    a class that does not count mirrors: the same amount within ``NET_TOLERANCE``,
    0–``NET_DAYS`` days apart, on any account of the customer.

    Each non-counted leg is spread over the days it can mirror, so the match is an
    equi-join on customer, day and direction (never all legs of a customer against all).
    """
    counted = F.col("flow_class").isin(*MONEY_IN_CLASSES, *MONEY_OUT_CLASSES)
    days = F.sequence(
        F.date_sub("tran_date", NET_DAYS), F.date_add("tran_date", NET_DAYS)
    )
    mirrors = legs.filter(~counted & (F.col("flow_class") != "salary")).select(
        F.col("cif_id").alias("_cif"),
        F.explode(days).alias("_day"),
        F.when(F.col("tran_dc") == "C", "D")
        .when(F.col("tran_dc") == "D", "C")
        .alias("_dc"),
        F.col("amount").alias("_amt"),
    )
    hit = (
        (F.col("cif_id") == F.col("_cif"))
        & (F.col("tran_date") == F.col("_day"))
        & (F.col("tran_dc") == F.col("_dc"))
        & (F.abs(F.col("_amt") - F.col("amount")) <= NET_TOLERANCE * F.col("amount"))
    )
    mirrored = (
        legs.filter(counted)
        .join(mirrors, hit, "leftsemi")
        .select("cif_id", "tran_id", "tran_date", "tran_dc")
    )
    return legs.join(
        mirrored, on=["cif_id", "tran_id", "tran_date", "tran_dc"], how="left_anti"
    )


```

2. **Split the node in two, with the legs saved to HDFS** (user, 2026-11-11): this cuts the
   lineage, avoids the triple read without caching, and lets a failed run restart from the legs.
   - `build_casa_flow_legs(transactions, casa_accounts, labelled, persona_start_date,
     history_months)` → **`prm_casa_flow_legs`**: one row per classified leg (`cif_id`, `tran_id`,
     `tran_date`, `tran_dc`, `amount`, `flow_class`, plus whatever columns your version needs
     downstream; drop the rest). Catalog entry in `catalog_casa.yml` beside `prm_casa_transactions`,
     same pattern (`${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/flow_legs`,
     parquet, overwrite, `partitionBy: ["event_month"]` with `event_month` = the leg's month, or
     whatever `prm_casa_transactions` uses).
   - `build_casa_flows(legs)` → `feat_cif_casa_flows_monthly`: `_net_mirrored` + the monthly
     aggregate, output columns unchanged.
   - Both nodes stay in `pipelines/casa/features.py` (explicit `func=`, `inputs=`, `outputs=`,
     `name=`, `tags=`); update the module docstring diagram.

## Hard rules

- Kedro I/O through node inputs/outputs only; `model_id` from globals; no `kedro run` in UAT.
- No change to any class rule, `NET_DAYS`, `NET_TOLERANCE`, or the output columns of
  `feat_cif_casa_flows_monthly`.
- Touch only `feat_cif_casa.py`, `pipelines/casa/features.py`, `catalog_casa.yml` and the tests.

## Deliverables

1. The two changes; `test_feat_cif_casa_flows.py` updated for the split and passing, plus one test
   that a counted leg mirrored 3 days later by a non-counted opposite leg (amount within 1%) is
   dropped and one 4 days later is kept; black / pylint clean.
2. The PROD run commands for the user, smallest first:
   `kedro run --pipeline=casa_features --nodes=build_prm_casa_flow_legs` (or your node name), then
   the flows node, then `product_features` and `crx_<p>_a1_check` as in bundle 21's step 6.
3. A short "Performance fix" section appended to `data/input/a1_bundle21_apply_summary.md`: what
   changed, the new node / dataset names, test results.
