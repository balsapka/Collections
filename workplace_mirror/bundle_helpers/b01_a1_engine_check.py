"""Bundle 01 PROD check: CC A1 ability before vs after the shared-engine refactor.

Lives in data/input/mirror_bundles/ (gitignored) — never commit it. Run in a Kedro
notebook (``catalog`` defined):

    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "data" / "input" / "mirror_bundles"))
    from b01_a1_engine_check import main

    main(catalog, step="snapshot")  # BEFORE re-running A1: copies the current output
    # ... run crx_cc_obs_base and crx_cc_a1_ability_v2 ...
    main(catalog, step="compare")   # old vs new, prints the B01 OUTPUT block
    main(catalog, step="cleanup")   # deletes the snapshot copy

The snapshot is a parquet copy on HDFS next to the A1 output (``<path>__pre_b01``), so no
catalog entry is needed. Results (aggregates only) go to
data/input/mirror_bundles/results/.
"""

import datetime
import json
import pathlib
import re

DS = "crx_cc_a1_ability_v2"
GRAIN = ["account_id", "observation_date"]


def _dataset_path(catalog) -> str:
    """Filesystem path of the A1 output dataset (Kedro 0.18 / 0.19 / 1.x)."""
    getter = getattr(catalog, "_get_dataset", None) or getattr(catalog, "get", None)
    ds = getter(DS)
    for attr in ("_filepath", "filepath", "_path"):
        path = getattr(ds, attr, None)
        if path:
            return str(path).rstrip("/")
    raise RuntimeError(f"cannot read the filepath of {DS}; describe(): {ds._describe()}")


def _snapshot_path(catalog) -> str:
    return _dataset_path(catalog) + "__pre_b01"


def _counts(df, col):
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def main(catalog, step="compare"):
    from pyspark.sql import functions as F

    model_id = catalog.load("params:model_id")  # ${globals:model_id}
    print(f"model_id={model_id}  step={step}")
    current = catalog.load(DS)
    spark = current.sparkSession
    snap = _snapshot_path(catalog)

    if step == "snapshot":
        if "a1_state_v2" not in current.columns:
            raise ValueError(f"{DS} already has the new schema — snapshot too late")
        current.select(*GRAIN, "a1_state_v2").write.mode("overwrite").parquet(snap)
        print(f"saved {spark.read.parquet(snap).count()} rows to {snap}")
        return None

    if step == "cleanup":
        jvm = spark.sparkContext._jvm
        path = jvm.org.apache.hadoop.fs.Path(snap)
        fs = path.getFileSystem(spark.sparkContext._jsc.hadoopConfiguration())
        print(f"deleted {snap}: {fs.delete(path, True)}")
        return None

    if "a1_state" not in current.columns:
        raise ValueError(f"{DS} still has the old schema — run the pipeline first")
    old = spark.read.parquet(snap).withColumnRenamed("a1_state_v2", "old_state")
    both = (
        current.select(
            *GRAIN,
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
        )
        .join(old, GRAIN, "full")
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    crosstab = [
        {"old": r["old_state"], "new": r["new_state"], "rows": r["count"]}
        for r in both.groupBy("old_state", "new_state")
        .count()
        .orderBy("old_state", "new_state")
        .collect()
    ]
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    payload = {
        "task": "B01_a1_engine",
        "run_date": datetime.date.today().isoformat(),
        "model_id": model_id,
        "scope": f"{snap} (pre-refactor output) vs {DS} (shared engine)",
        "results": {
            "rows": n,
            "changed": changed,
            "changed_pct": round(100.0 * changed / max(n, 1), 2),
            "old_states": _counts(both, "old_state"),
            "new_states": _counts(both, "new_state"),
            "new_income_levels": _counts(both, "a1_income_level"),
            "new_liquidity_levels": _counts(both, "a1_liquidity_level"),
            "crosstab": crosstab,
        },
    }
    out = pathlib.Path(__file__).resolve().parent / "results"
    out.mkdir(parents=True, exist_ok=True)
    tag = re.sub(r"[^A-Za-z0-9]+", "_", str(model_id))
    path = out / f"B01_a1_engine_{tag}_{payload['run_date'].replace('-', '')}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))

    print("=== B01 OUTPUT START ===")
    pct = payload["results"]["changed_pct"]
    print(f"model_id={model_id} rows={n} changed={changed} ({pct}%)")
    for name in ("new_income_levels", "new_liquidity_levels"):
        print(f"  {name}: {payload['results'][name]}")
    for row in crosstab:
        print(f"  {row['old']:<18} -> {row['new']:<18} {row['rows']:>9}")
    print("=== B01 OUTPUT END ===")
    print(f"written: {path}")
    return payload
