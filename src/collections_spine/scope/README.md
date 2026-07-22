# Config-driven scope filtering (staging side)

> **If you are a fresh Claude Code session picking this up:** read the *Intent* and
> *Invariants* sections first. They are the point. The rest is API detail.

## Intent — what this refactoring is for

We run a layered Kedro + Spark pipeline over billion-row raw tables, but the real
modelling population is a small fraction of them. Every raw table must be reduced
to the in-scope rows **before** any feature logic runs. The refactoring goal is to
make that reduction:

1. **Selectivity-first** — prune to the in-scope ids (a broadcastable set) before
   any date logic or heavy shuffle, never after.
2. **Computed once** — the scope sets are built once upstream and persisted; a
   staging node never rebuilds them.
3. **Config-driven, not code-duplicated** — each raw table declares *how* it is
   scoped (which id type, which strategy, which date column) as data; the join
   machinery is written once in `apply_scope`.
4. **Contained** — scope wiring lives only in the staging layer. Downstream
   primary / intermediate / feature pipelines read staged outputs and never see a
   scope dataset.

The anti-pattern we are moving away from: reducing the universe *last* (join the
whole raw table to a full spine, then filter), and recomputing
`spine.select(id).distinct()` inside every node (the same shuffle, N times).

## The layers

| Layer | Reads | Scope wiring? |
|-------|-------|---------------|
| **spine** | raw (slim) | produces `*_scope_ids` / `*_windows` / `*_grid` **once** (your own builders) |
| **staging** | raw | `scoped_stage` per table (strategy + scope are config) |
| primary / intermediate / feature | previous layer only | none — raw-free, so scope-free |

**This module is the staging side only.** The scope sets are produced upstream
(spine layer / your own functions, including your `data_scope_ids` grid builder),
persisted, and passed to staging nodes as catalog inputs. `apply_scope` **never**
calls `.distinct()` — it only *joins* pre-built sets.

## Multiple id types — there is no single global scope

There are **many** scope sets, one per id type: a customer-grain `customer_scope_ids`
(+ `customer_windows` / `customer_grid`), an account-grain `account_scope_ids`, and
so on. Each staging node picks **its own** `id_col` and **its own** scope datasets to
match the grain of its raw table. Nothing about `apply_scope` assumes a single
scope — `id_col` and the scope DataFrames are per-node arguments. See
`pipeline.py`: `stage_txns` uses the customer scope, `stage_positions` uses the
account scope, in the same pipeline.

When you add an id type, you add its scope datasets to the catalog and point the
relevant nodes at them. No code in this module changes.

## Strategies (per table, chosen in config)

- `id_only` — `leftsemi` on `scope_ids`. Small dims / no date reduction.
- `range` — `leftsemi` against `windows` `(id, win_start, win_end)`;
  `date BETWEEN win_start AND win_end`. Per-id windows live in two columns, nothing
  materialised at row grain. Works regardless of partitioning. **Default choice.**
- `grid` — equi `leftsemi` on `(id, <grid_col>)`. Use **only** when the raw table is
  physically partitioned on that grain (enables dynamic partition pruning);
  otherwise `range` is cheaper. `grain` truncates the raw date to match the grid;
  `grain=None` for a daily enumerated grid (exact match).

## Invariants — do not regress these when refactoring further

1. **Never `.distinct()` (or otherwise rebuild a scope set) inside a staging node.**
   Scope sets are inputs, built once upstream. Rebuilding = the same shuffle N times.
2. **The precise match is always `leftsemi`.** A raw row covered by several
   overlapping anchor windows must survive **exactly once** — no fan-out, no dedup.
   An inner join would duplicate it.
3. **Only `scope_ids` is force-broadcast.** `windows` / `grid` are one row per
   `(id, anchor)` / `(id, grain)` and can be **millions** of rows; forcing a
   broadcast collects them to the driver and OOMs. Leave `broadcast_scope=False`.
4. **`range` relies on the equi `id` key.** That is what makes Spark run it as a
   sort-merge join with `BETWEEN` as a residual filter, *not* a cartesian. Keep the
   equi condition on `id_col`.
5. **Scope is reduction only.** Grain / as-of / point-in-time logic belongs in the
   downstream transform, never in `apply_scope`.

## Broadcasting

Only `scope_ids` (one row per id) is force-broadcast by default (`broadcast_ids`).
`windows` and `grid` are **not** (invariant 3). Left unhinted, the `range` join is a
sort-merge join on the equi `id` key with the `BETWEEN` as a residual filter, and
Spark still auto-broadcasts either side if it is genuinely under
`spark.sql.autoBroadcastJoinThreshold`. Pass `broadcast_scope=True` only for a known
small set (e.g. a single-anchor population).

## Catalog — one set of scope datasets PER id type

```yaml
# --- customer-grain scope (built upstream by your spine-layer nodes) ---------
customer_scope_ids:       # (customer_id)
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/customer_scope_ids.parquet
  file_format: parquet
  save_args: {mode: overwrite}

customer_windows:         # (customer_id, win_start, win_end) — only if you use `range`
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/customer_windows.parquet
  file_format: parquet
  save_args: {mode: overwrite}

# --- account-grain scope (a DIFFERENT id type) -------------------------------
account_scope_ids:        # (account_id)
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/account_scope_ids.parquet
  file_format: parquet
  save_args: {mode: overwrite}

account_grid:             # (account_id, obs_month) — YOUR data_scope_ids builder
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/account_grid.parquet
  file_format: parquet
  save_args: {mode: overwrite, partitionBy: [obs_month]}

# --- staged outputs ----------------------------------------------------------
txns_staged:
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../03_primary/txns_staged.parquet
  file_format: parquet
  save_args: {mode: overwrite}
# ... positions_staged, customer_dim_staged likewise
```

## Adding a raw table

One `node(func=partial(scoped_stage, ...), ...)` entry in the staging pipeline:
pick the `id_col` for that table's grain, the `strategy`, the `date_col`, and wire
only the scope sets that strategy needs (of the matching id type). Nothing else in
the codebase changes.

## Column-name assumptions (adjust to your builders)

- `windows` must have columns literally named `win_start` and `win_end`. Alias them
  in your builder, or make those configurable in `apply_scope` if you prefer.
- `grid`'s grain column name is configurable via `grid_col` (default `obs_month`).

## Run order

Scope sets feed staging; keep the dependency explicit in the DAG, or sequence the
pipelines in your orchestrator (build scope sets, then `kedro run --pipeline
staging`). Scope changes only when the modelling window or population moves, so
treat the scope sets as slowly-changing persisted artifacts.
