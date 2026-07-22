# Config-driven scope filtering (staging side)

Reduce every wide raw table to the modelling scope, with each table choosing its
own strategy — without recomputing scope sets or littering feature nodes.

## The layers

| Layer | Reads | Scope wiring? |
|-------|-------|---------------|
| **spine** | raw (slim) | produces `scope_ids` / `scope_windows` / `scope_grid` **once** (your own builders) |
| **staging** | raw | `scoped_stage` per table (strategy is config) |
| primary / intermediate / feature | previous layer only | none — raw-free, so scope-free |

This module is the **staging side only**. The scope sets are produced upstream
(spine layer / your own functions), persisted, and passed to staging nodes as
catalog inputs. `apply_scope` **never** calls `.distinct()` — it only *joins*
pre-built sets, so N staging nodes don't shuffle the same set N times.

## Strategies

- `id_only` — `leftsemi` on `scope_ids`. Small dims / no date reduction.
- `range` — `leftsemi` against `windows` `(id, win_start, win_end)`;
  `date BETWEEN win_start AND win_end`. Per-id windows live in two columns, nothing
  materialised at row grain. Works regardless of partitioning. **Default.**
- `grid` — equi `leftsemi` on `(id, <grid_col>)`. Use **only** when the raw table
  is physically partitioned on that grain (enables dynamic partition pruning).
  `grain` truncates the raw date to match; `grain=None` for a daily enumerated grid.

The precise match is always `leftsemi`, so a raw row covered by several anchors
survives exactly once — no fan-out, no dedup. Grain / as-of logic belongs in the
downstream transform, not in scope.

## Broadcasting

Only `scope_ids` (one row per id) is force-broadcast by default (`broadcast_ids`).
`windows` and `grid` are **not** — they're one row per `(id, anchor)` / `(id, grain)`
and can be millions of rows, so forcing a broadcast collects them to the driver and
OOMs. Left unhinted, the `range` join runs as a sort-merge join on the equi `id`
key with the `BETWEEN` as a residual filter (the equi key means it's never a
cartesian), and Spark still auto-broadcasts either side if it's genuinely under
`spark.sql.autoBroadcastJoinThreshold`. Pass `broadcast_scope=True` only for a
small set (e.g. a single-anchor population).

## Catalog (staged outputs; scope sets defined wherever you build them)

```yaml
scope_ids:        # (entity_id) — your builder
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/scope_ids.parquet
  file_format: parquet
  save_args: {mode: overwrite}

scope_windows:    # (entity_id, win_start, win_end) — only if you use `range`
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/scope_windows.parquet
  file_format: parquet
  save_args: {mode: overwrite}

scope_grid:       # (entity_id, obs_month) — YOUR data_scope_ids builder
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/scope_grid.parquet
  file_format: parquet
  save_args: {mode: overwrite, partitionBy: [obs_month]}

txns_staged:
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../03_primary/txns_staged.parquet
  file_format: parquet
  save_args: {mode: overwrite}
# ... events_staged, dim_staged likewise
```

## Adding a raw table

One `node(func=partial(scoped_stage, ...), ...)` entry in the staging pipeline —
pick `strategy`, `id_col`, `date_col`, and wire only the scope sets that strategy
needs. Nothing else in the codebase changes.

## Run order

Scope sets feed staging; keep the dependency explicit in the DAG, or sequence the
pipelines in your orchestrator (build scope sets, then `kedro run --pipeline
staging`). Scope changes only when the modelling window or population moves, so
treat the scope sets as slowly-changing persisted artifacts.
