# Config-driven scope filtering

Reduce every wide raw table to the modelling scope, with each table choosing its
own strategy — without recomputing scope sets or littering feature nodes.

## The layers

| Layer | Reads | Scope wiring? |
|-------|-------|---------------|
| **spine** | raw (slim) | builds `scope_ids` / `scope_windows` / `scope_grid` **once** |
| **staging** | raw | `scoped_stage` per table (strategy is config) |
| primary / intermediate / feature | previous layer only | none — raw-free, so scope-free |

## The one rule

`apply_scope` **never** calls `.distinct()`. The distinct id set, the per-anchor
windows, and the exploded grid are built once in the spine layer and persisted;
staging nodes only *join* them. That's what keeps N staging nodes from shuffling
the same set N times.

## Strategies

- `id_only` — broadcast `leftsemi` on `scope_ids`. Small dims / no date reduction.
- `range` — broadcast `leftsemi` against `(id, win_start, win_end)`;
  `date BETWEEN win_start AND win_end`. Per-id windows live in two columns, nothing
  materialised at row grain. Works regardless of partitioning. **Default.**
- `grid` — equi `leftsemi` on `(id, obs_grain)`. Use **only** when the raw table is
  physically partitioned on that grain (enables dynamic partition pruning).

The precise match is always `leftsemi`, so a raw row covered by several anchors
survives exactly once — no fan-out, no dedup. Grain / as-of logic belongs in the
downstream transform, not in scope.

## Catalog (persist the scope sets — narrow, reused everywhere)

```yaml
modelling_spine:                     # (entity_id, anchor_date) — built upstream
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/modelling_spine.parquet
  file_format: parquet

scope_ids:
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/scope_ids.parquet
  file_format: parquet
  save_args: {mode: overwrite}

scope_windows:
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/scope_windows.parquet
  file_format: parquet
  save_args: {mode: overwrite}

scope_grid:
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/scope_grid.parquet
  file_format: parquet
  save_args: {mode: overwrite, partitionBy: [obs_grain]}

txns_staged:
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../03_primary/txns_staged.parquet
  file_format: parquet
  save_args: {mode: overwrite}
# ... events_staged, dim_staged likewise
```

## Adding a raw table

One `node(func=partial(scoped_stage, ...), ...)` entry in the staging pipeline —
pick `strategy`, `on`, `date_col`, and wire only the scope sets that strategy
needs. Nothing else in the codebase changes.

## Run order

Scope sets feed staging, but if you later hide scoping inside a custom dataset the
DAG can't see that edge — keep it explicit (as here) or sequence the pipelines in
your orchestrator: `kedro run --pipeline scope` then `--pipeline staging`. Scope
changes only when the modelling window or population moves, so treat the scope
sets as slowly-changing persisted artifacts.
```
