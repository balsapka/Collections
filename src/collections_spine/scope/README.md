# Scope filtering (staging side)

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
3. **Small and composable** — three tiny leftsemi filters, each taking only the
   arguments its join shape needs. Per-table facts (column names, which filters
   apply) live in that table's own staging function, not in shared machinery.
   There is deliberately NO strategy enum, NO factory, NO mega-function.
4. **Contained** — scope wiring lives only in the staging layer. Downstream
   primary / intermediate / feature pipelines read staged outputs and never see a
   scope dataset.

Anti-patterns we moved away from: reducing the universe *last* (join the whole raw
table to a full spine, then filter); recomputing `spine.select(id).distinct()`
inside every node (the same shuffle, N times); one `apply_scope(strategy=...)`
function with 12 parameters of which any call used 4.

## The layers

| Layer | Reads | Scope wiring? |
|-------|-------|---------------|
| **spine** | raw (slim) | produces `*_scope_ids` / `*_windows` / `*_pairs` **once** (your own builders) |
| **staging** | raw | per-table staging function composes the filters it needs |
| primary / intermediate / feature | previous layer only | none — raw-free, so scope-free |

## The API — three composable filters

```python
from collections_spine.scope import filter_ids, filter_windows, filter_pairs

def stage_txns(raw, scope_ids, windows):
    df = raw.where(F.col("load_date").between(LO, HI))       # coarse prune: plain where
    df = filter_ids(df, scope_ids, id_col="contract_idt",
                    scope_id_col="customer_id")               # id in scope
    df = filter_windows(df, windows, id_col="contract_idt",
                        date_col="txn_date", scope_id_col="customer_id")
    ...                                                       # real staging logic
    return df
```

- `filter_ids(df, scope_ids, id_col=..., scope_id_col=None, broadcast=True)` —
  keep rows whose id is in scope. Broadcast leftsemi.
- `filter_windows(df, windows, id_col=..., date_col=..., scope_id_col=None,
  start_col="win_start", end_col="win_end")` — keep rows whose date falls in ANY
  of the id's anchor windows `(id, start, end)`. Equi id + `BETWEEN` residual →
  sort-merge join, never a cartesian. Works regardless of partitioning. **Default.**
- `filter_pairs(df, pairs, id_col=..., date_col=..., scope_id_col=None,
  scope_date_col=None)` — keep rows whose exact `(id, date)` pair is in scope.
  **Always joins on both id and date** — no grain/truncation knobs; build the pair
  set at the raw table's grain upstream. Use only when the raw table is physically
  partitioned on the date grain (the equi key enables dynamic partition pruning);
  otherwise `filter_windows` is cheaper.

The coarse partition prune (`load_date BETWEEN ...`) is a plain `.where()` in the
staging function — it needs no helper.

## Column-name mapping, not dataset copies

Raw tables and scope sets rarely share column names, and there are MANY scope sets
(one per id type: `customer_scope_ids`, `account_scope_ids`, ...). Every filter
takes `scope_*_col` names and aliases the **small side** internally — an alias is
a projection in the Spark plan, so nothing is materialised. **Never create a
renamed copy of a scope/spine dataset just to match a raw table's columns.**

## Multiple id types — there is no single global scope

Each id type has its own scope sets, produced upstream by your builders. A staging
node names the ones matching its table's grain in its Kedro `inputs` — see
`pipeline.py`, where `stage_txns` uses the customer sets and `stage_positions`
uses the account sets in the same pipeline. Adding an id type = adding its scope
datasets to the catalog; no code here changes.

## SCD2 / interval tables — reduction is not enough

The filters above are **grain-preserving**: they keep in-scope raw rows as they
are. That is correct for daily-grain and event tables and **wrong** for SCD2 /
effective-dated tables (`eff_start`/`eff_end` intervals), which need a
**grain-changing** step: collapse each id's interval history to **one active row
per `(id, observation_date)`** — the state as-of each date. That is
`stage_scd2_table` / `prefilter_scd2` in the parent package (interval covering the
date, greatest `eff_start`, `date_modified` only as a restatement tie-break).

| | `filter_windows` / `filter_pairs` | SCD2 (`stage_scd2_table`) |
|---|---|---|
| question | *gather a window of history* | *state as-of each observation date* |
| output grain | raw rows in scope | one row per `(id, observation_date)` |
| operation | grain-preserving `leftsemi` | interval → point-in-time collapse |

```python
node(
    func=partial(stage_scd2_table, schema=Scd2Schema(key="customer_id"),
                 broadcast_accounts=True),
    inputs={"raw_df": "raw_customer_scd2",
            "spine": "customer_pairs",         # the (id, observation_date) pairs
            "accounts": "customer_scope_ids"}, # pre-built ids -> no per-node distinct
    outputs="customer_scd2_staged", name="stage_customer_scd2",
)
```

It consumes the **same** `customer_scope_ids` (via `accounts=`) as the reduction
filters, so the id set is still computed once.

## Invariants — do not regress these when refactoring further

1. **Never `.distinct()` (or otherwise rebuild a scope set) inside a staging
   node.** Scope sets are inputs, built once upstream.
2. **Every filter is a `leftsemi`.** A raw row covered by several overlapping
   anchor windows must survive **exactly once** — an inner join would duplicate it.
3. **Only the id set is force-broadcast.** `windows` / `pairs` are one row per
   `(id, anchor)` / `(id, date)` and can be **millions** of rows; a forced
   broadcast collects them to the driver and OOMs. Spark auto-broadcasts a
   genuinely small side on its own.
4. **`filter_windows` relies on the equi id key.** That is what makes Spark run a
   sort-merge join with `BETWEEN` as a residual filter, *not* a cartesian.
5. **Map column names by aliasing the small side, never by copying datasets.**
6. **Scope is reduction only.** Grain / as-of / point-in-time logic belongs in
   `stage_scd2_table` or the downstream transform, never in these filters.

## Catalog — one set of scope datasets PER id type

```yaml
# --- customer-grain scope (built upstream by your spine-layer nodes) ---------
customer_scope_ids:       # (customer_id)
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/customer_scope_ids.parquet
  file_format: parquet
  save_args: {mode: overwrite}

customer_windows:         # (customer_id, win_start, win_end)
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/customer_windows.parquet
  file_format: parquet
  save_args: {mode: overwrite}

customer_pairs:           # (customer_id, observation_date)
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/customer_pairs.parquet
  file_format: parquet
  save_args: {mode: overwrite}

# --- account-grain scope (a DIFFERENT id type) -------------------------------
account_scope_ids:        # (account_id)
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/account_scope_ids.parquet
  file_format: parquet
  save_args: {mode: overwrite}

account_pairs:            # (account_id, obs_date) — YOUR data_scope_ids builder
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../02_intermediate/account_pairs.parquet
  file_format: parquet
  save_args: {mode: overwrite, partitionBy: [obs_date]}

# --- staged outputs ----------------------------------------------------------
txns_staged:
  type: spark.SparkDataSet
  filepath: hdfs:///proj/.../03_primary/txns_staged.parquet
  file_format: parquet
  save_args: {mode: overwrite}
# ... positions_staged, customer_dim_staged, customer_scd2_staged likewise
```

## Adding a raw table

Write one small staging function composing the filters it needs, register one
`node(...)` pointing at that table's scope datasets. Nothing else changes.

## Run order

Scope sets feed staging; keep the dependency explicit in the DAG, or sequence the
pipelines in your orchestrator (build scope sets, then `kedro run --pipeline
staging`). Scope changes only when the modelling window or population moves, so
treat the scope sets as slowly-changing persisted artifacts.
