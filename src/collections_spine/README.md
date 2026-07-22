# collections_spine

Spine-driven staging utilities for the Collections risk-modeling Kedro pipelines.

Reduce every billion-row source table to the exact `(account_id, observation_date)`
pairs your data scientists need **before** any feature logic runs, so Kedro nodes
never transform the full universe.

> **Config-driven scope filtering** (the current refactoring — per-table strategy,
> multiple id types, no recomputed `distinct()`) lives in [`scope/`](scope/README.md).
> Start there for the staging-layer reduction pattern; this README covers the older
> SCD2 / daily prefilter helpers.

## Concepts

- **Spine** — the `(account_id, observation_date)` backbone. `observation_date` is
  a small discrete set (e.g. month-ends). That smallness is what makes this fast.
- **Daily-grain tables** `(account_id, snapshot_date, ...)` — matched exactly
  (`snapshot_date == observation_date`) or as-of (latest snapshot on/before).
- **SCD2 tables** `(account_id, effective_start_date, effective_end_date,
  date_modified, ...)` — the active record is the one whose half-open interval
  `[start, end)` contains the observation date; among those the greatest
  `effective_start_date` wins, and `date_modified` only breaks a tie between
  restatements of the same interval (latest wins). `date_modified` is **not** a
  knowledge cutoff — a correction booked after the observation date is still
  used; filter `date_modified <= observation_date` upstream yourself if you need
  leakage-free point-in-time selection. Open records use the estate-wide sentinel
  `effective_end_date = 2100-01-01`, baked into `Scd2Schema`'s defaults.

## Reduction pipeline

```
0. account semi-join     -> drop accounts outside the modeling population
1. date-overlap prune    -> partition pruning on date-partitioned tables
2. grid join to distinct -> broadcast the tiny observation-date set; the interval
   observation dates         join becomes a bounded explode
3. restatement dedup     -> one row per (account_id, observation_date)
4. equi-join to spine    -> exact pairs only
```

## Usage

```python
from collections_spine import (
    Scd2Schema, build_spine, prefilter_scd2, prefilter_daily, active_as_of,
)

spine = build_spine(accounts_df, ["2025-12-31", "2026-01-31", "2026-02-28"])

limits  = prefilter_scd2(raw_limits, spine)                 # SCD2 (estate defaults)
balance = prefilter_daily(raw_balances, spine)              # exact snapshot match
score   = prefilter_daily(raw_scores, spine, asof=True, lookback_days=45)

# single-date active record (greatest eff_start, latest restatement as tie-break)
snap = active_as_of(raw_limits, "2026-01-31")
```

### Selection rule (and leakage)

Both `prefilter_scd2` and `active_as_of` select, per `(key, observation_date)`,
the covering interval with the greatest `effective_start_date`, using
`date_modified` only to break a tie between restatements of the same interval.

`date_modified` is **not** treated as a knowledge cutoff: a correction booked
after the observation date is still applied (in this estate `date_modified` is a
load/restatement timestamp, typically later than the observation date). If you
need leakage-free training sets, filter `date_modified <= observation_date`
yourself before staging.

## Kedro wiring

```python
# pipeline.py
from kedro.pipeline import Pipeline, node
from collections_spine import build_spine, stage_scd2_table, stage_daily_table

def create_pipeline(**_) -> Pipeline:
    return Pipeline([
        node(build_spine, ["accounts", "params:observation_dates"], "spine"),
        node(stage_scd2_table,  ["raw.limits",   "spine"], "staging.limits"),
        node(stage_daily_table, ["raw.balances", "spine"], "staging.balances"),
        # ... one node per source table, all reading `spine`, all writing small outputs
    ])
```

```yaml
# catalog.yml — partition staged outputs by observation_date for free pruning
staging.limits:
  type: spark.SparkDataSet
  filepath: data/02_staging/limits.parquet
  file_format: parquet
  save_args: { mode: overwrite, partitionBy: [observation_date] }
```

```yaml
# parameters.yml
observation_dates: ["2025-12-31", "2026-01-31", "2026-02-28"]
```

For a daily table that needs as-of matching, partial-apply the node arguments:

```python
from functools import partial
node(partial(stage_daily_table, asof=True, lookback_days=45),
     ["raw.scores", "spine"], "staging.scores")
```

## Performance levers (biggest wins first)

1. **Physical layout (one-time):** bucket / Z-order the raw tables by `account_id`
   and partition by their date column. The account semi-join and the final spine
   join then become shuffle-free; Spark's dynamic partition pruning kicks in.
2. **Broadcast only the tiny sides:** distinct observation dates always; distinct
   accounts (`broadcast_accounts=True`) only if they fit in memory.
3. **Push the semi-join to node 0** — never derive/cast over the full universe
   before the spine filter. Do feature logic in the primary layer on staged data.
4. **Skew:** salt the dedup key or filter sentinel/test accounts if a few keys are
   hot.

## Watch-outs

- **Interval convention:** default is half-open `[start, end)`. If your
  `effective_end_date` is the *last valid day*, set `Scd2Schema(end_inclusive=True)`
  or you will drop/double-count boundary-day records.
- **Exact vs as-of daily:** if observations don't always land on a snapshot date,
  use `asof=True` (with a `lookback_days` bound).
- **Open-ended (sentinel) SCD2 tables:** `prefilter_scd2` already orders by
  `eff_start` first, so it picks the latest `eff_start <= obs` correctly even when
  *every* record carries a sentinel `eff_end`. But its interval grid join still
  fans each record out to every covered observation date, which is wasteful at
  billion-row scale — prefer the exact-match/anchor-prune pattern in
  `nodes/spine_builders.py::contract_pit` for those tables (performance, not
  correctness).

## DLQ contract spine (`nodes/spine_builders.py`)

Selectivity-first rebuild of the old `build_contract_spine`. Final dataset:
distinct `(contract_idt, observation_date, cif_id, dlq_bucket_from_hist)`, over a
billion-row SCD2 `contract` table (latest `record_date_from`-wins; `record_date_to`
always the `2100-01-01` sentinel) and a billion-row daily `billing` table
partitioned on `edp_load_date`.

Progressive narrowing, each stage a persisted node:

```
slim_contract -> dlq_candidate_ids -> build_billing_spine -> contract_pit
  -> contract_dlq ──┬─> dlq_spine ─────────────> stage_contract_attribute ─┐
                    └─> enrich_product ──────────────────> apply_collateral ┘
                          (product scope)                   (collateral scope)
                              -> build_client_spine -> stage_client
                              -> finalize_contract_spine  (attach cif_id) => contract_spine
```

`stage_contract_attribute` / `stage_client` call your existing `_stg_ca.build` /
`_stg_client.build` on the narrowed spine (adjust the imports in
`nodes/spine_builders.py`). Provided as ready-to-run Kedro files:

- pipeline: [`pipelines/dlq_spine/pipeline.py`](pipelines/dlq_spine/pipeline.py)
- datasets: [`conf/base/catalog.yml`](../../conf/base/catalog.yml)
- params: [`conf/base/parameters.yml`](../../conf/base/parameters.yml)

Register it in your `pipeline_registry.py`:

```python
from src.collections_spine.pipelines.dlq_spine import create_pipeline as dlq_spine

def register_pipelines():
    dlq = dlq_spine()
    return {"dlq_spine": dlq, "__default__": dlq}
```

```yaml
# conf/base/parameters.yml
modelling:
  start_date: "2024-01-01"
  end_date:   "2026-06-30"
  scope_filtering:
    dlq_min: 4
    dlq_max: 7
    collateral_codes: []                  # TODO: codes kept by apply_collateral
  billing_load_date_col: edp_load_date    # the daily PARTITION column on billing
  billing_cycle_buffer_days: 35           # >= one billing cycle (see note below)
```

```yaml
# conf/base/catalog.yml — persist intermediates to HDFS; reruns read narrow parquet
contract_slim:      {type: spark.SparkDataSet, filepath: "hdfs:///proj/collections/02_intermediate/contract_slim.parquet",     file_format: parquet, save_args: {mode: overwrite}}
dlq_candidate_ids:  {type: spark.SparkDataSet, filepath: "hdfs:///proj/collections/02_intermediate/dlq_candidate_ids.parquet", file_format: parquet, save_args: {mode: overwrite}}
billing_spine:      {type: spark.SparkDataSet, filepath: "hdfs:///proj/collections/02_intermediate/billing_spine.parquet",     file_format: parquet, save_args: {mode: overwrite, partitionBy: [observation_date]}}
contract_pit:       {type: spark.SparkDataSet, filepath: "hdfs:///proj/collections/03_primary/contract_pit.parquet",          file_format: parquet, save_args: {mode: overwrite, partitionBy: [observation_date]}}
dlq_spine:          {type: spark.SparkDataSet, filepath: "hdfs:///proj/collections/03_primary/dlq_spine.parquet",             file_format: parquet, save_args: {mode: overwrite}}
```

**`billing_cycle_buffer_days`** must be ≥ your longest billing cycle. A `billing_date`
only appears in load partitions from its cycle onward, so to capture dates near
`end_date` we read `edp_load_date` up to `end_date + buffer`.

**Checking the partition column of an HDFS dataset:** inspect the directory layout —
`hdfs dfs -ls <filepath>` shows `edp_load_date=YYYY-MM-DD/` subdirectories for a
partitioned parquet path; for a Hive table use `SHOW PARTITIONS db.table` or
`DESCRIBE FORMATTED db.table` (look for the `# Partition Information` block).
