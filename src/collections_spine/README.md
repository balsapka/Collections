# collections_spine

Spine-driven staging utilities for the Collections risk-modeling Kedro pipelines.

Reduce every billion-row source table to the exact `(account_id, observation_date)`
pairs your data scientists need **before** any feature logic runs, so Kedro nodes
never transform the full universe.

## Concepts

- **Spine** — the `(account_id, observation_date)` backbone. `observation_date` is
  a small discrete set (e.g. month-ends). That smallness is what makes this fast.
- **Daily-grain tables** `(account_id, snapshot_date, ...)` — matched exactly
  (`snapshot_date == observation_date`) or as-of (latest snapshot on/before).
- **SCD2 tables** `(account_id, effective_start_date, effective_end_date,
  date_modified, ...)` — the active record is the one whose half-open interval
  `[start, end)` contains the observation date; `date_modified` restatements are
  de-duplicated by keeping the latest known correction. Open records use the
  estate-wide sentinel `effective_end_date = 2100-01-01`, baked into
  `Scd2Schema`'s defaults.

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

# single-date point-in-time, leakage-free (no future restatements)
snap = active_as_of(raw_limits, "2026-01-31", knowledge_date="2026-01-31")
```

### Leakage / point-in-time correctness

`prefilter_scd2(..., respect_knowledge_time=True)` (default) drops corrections
booked *after* the observation date. Keep it on for training-set staging so a row
reflects only what was known as of `observation_date`.

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
