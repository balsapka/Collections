"""Bundle 01 PROD check: CC A1 ability before vs after the shared-engine refactor.

Run in a Kedro notebook (``catalog`` defined), in this order:

    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "docs" / "context" / "snippets"))
    from b01_a1_engine_check import main

    main(catalog, step="snapshot")   # 1. BEFORE re-running A1: keeps the current output
    # 2. kedro run --pipeline=crx_cc_obs_base
    #    kedro run --pipeline=crx_cc_a1_ability_v2
    result = main(catalog, step="compare")   # 3. old vs new

Aggregates only. Writes docs/context/results/B01_a1_engine_<model_id>_<date>.json and
prints the headline between the OUTPUT markers — paste that block back.
"""

import datetime
import json
import pathlib
import re

DS_NEW = "crx_cc_a1_ability_v2"
DS_OLD = "crx_cc_a1_ability_pre_refactor"
GRAIN = ["account_id", "observation_date"]


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "conf").is_dir():
            return parent
    raise RuntimeError(f"repo root not found above {here}")


def _counts(df, col):
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def main(catalog, step="compare", out_dir=None):
    from pyspark.sql import functions as F

    model_id = catalog.load("params:model_id")  # ${globals:model_id}
    print(f"model_id={model_id}  step={step}")

    if step == "snapshot":
        old = catalog.load(DS_NEW)
        if "a1_state_v2" not in old.columns:
            raise ValueError(f"{DS_NEW} already has the new schema — snapshot too late")
        catalog.save(DS_OLD, old.select(*GRAIN, "a1_state_v2"))
        print(f"saved {DS_OLD}: {catalog.load(DS_OLD).count()} rows")
        return None

    old = catalog.load(DS_OLD).withColumnRenamed("a1_state_v2", "old_state")
    new = catalog.load(DS_NEW)
    if "a1_state" not in new.columns:
        raise ValueError(f"{DS_NEW} still has the old schema — run the pipeline first")
    both = new.select(
        *GRAIN,
        F.col("a1_state").alias("new_state"),
        "a1_income_level",
        "a1_liquidity_level",
    ).join(old, GRAIN, "full")
    both = both.fillna({"old_state": "(absent)", "new_state": "(absent)"}).cache()

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
        "scope": f"{DS_OLD} (pre-refactor v2 output) vs {DS_NEW} (shared engine)",
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
    out = (
        pathlib.Path(out_dir)
        if out_dir
        else _repo_root() / "docs" / "context" / "results"
    )
    out.mkdir(parents=True, exist_ok=True)
    tag = re.sub(r"[^A-Za-z0-9]+", "_", str(model_id))
    path = out / f"B01_a1_engine_{tag}_{payload['run_date'].replace('-', '')}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))

    print("=== B01 OUTPUT START ===")
    print(
        f"model_id={model_id} rows={n} changed={changed} ({payload['results']['changed_pct']}%)"
    )
    for row in crosstab:
        print(f"  {row['old']:<18} -> {row['new']:<18} {row['rows']:>9}")
    print("=== B01 OUTPUT END ===")
    print(f"written: {path}")
    return payload
