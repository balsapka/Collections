"""DPD deterioration states — validation on real data (PROD).

Assigns the deterioration states (options A / B / C) to today's bucket 4–7 spine,
backtests them on the spine as of BACKTEST_MONTHS ago (outcomes read from the newer
digits of today's strings), measures overlap with the other persona axes, sweeps every
threshold, and checks each result against the written expectations (PASS / WARN / FAIL).

Run in a Kedro notebook where `catalog` exists. Works from any notebook location:

    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))

    from dpd_states_validate import main
    result = main(catalog, check_only=True)        # 1st: schema, counts, examples only
    result = main(catalog)                         # full run, model_id from globals_dev
    result = main(catalog, model_id="<variant>")   # or one variant explicitly

READ-ONLY: writes nothing to the warehouse. Writes one aggregates-only JSON (+ a markdown
report) to docs/deterioration_states/results/ — no account keys, no row-level data.
The markdown contains a handful of example DPD strings (no keys) for eyeballing.

FILL IN before running:
  * docs/deterioration_states/dpd_states/config.py — dataset and column names
  * _resolve_model_id below — the globals_dev accessor
Never guess a name: discover it in the repo catalog, or ask.

Sizes: the spine populations are sampled to `sample_n` rows each (default 100k) and only
the DPD string plus the configured optional columns are collected. The analysis itself
is pandas (the tested package in ../dpd_states).
"""
import datetime
import json
import pathlib
import re
import sys


def _pkg_root() -> pathlib.Path:
    """docs/deterioration_states — resolved from this file, independent of the CWD."""
    return pathlib.Path(__file__).resolve().parents[1]


def _resolve_model_id(model_id=None) -> str:
    """caller arg → project globals. Never a hardcoded literal."""
    if model_id:
        return model_id
    # <<FILL-IN: the real accessor — discover it in the workplace repo, never guess.
    #  Shape is one of:
    #    from <pkg>.<module> import globals_dev   ->  globals_dev["model_id"]
    #    conf_loader["globals"]["model_id"]  (Kedro OmegaConfigLoader) >>
    from FILL_IN_module_exposing_globals_dev import globals_dev  # noqa  <<FILL-IN>>
    return globals_dev["model_id"]                              # <<FILL-IN: key, if it differs>>


def _sample(sdf, n_rows, sample_n, seed):
    if not n_rows or n_rows <= sample_n:
        return sdf
    return sdf.sample(False, min(1.0, 1.1 * sample_n / n_rows), seed).limit(sample_n)


def main(catalog, model_id=None, out_dir=None, sample_n=100_000, check_only=False, seed=42):
    from pyspark.sql import functions as F

    sys.path.insert(0, str(_pkg_root()))
    from dpd_states import config as cfg
    from dpd_states.analysis import md, run
    from dpd_states.expectations import evaluate
    from dpd_states.states import DISPLAY_NAMES, OPTIONS, RECOMMENDED

    model_id = _resolve_model_id(model_id)
    out_dir = pathlib.Path(out_dir) if out_dir else _pkg_root() / "results"
    k = cfg.BACKTEST_MONTHS
    ds = cfg.DS_STRINGS_TMPL.format(model_id=model_id)

    unfilled = [n for n, v in (("DS_STRINGS_TMPL", ds), ("KEY", cfg.KEY), ("COL_DPD", cfg.COL_DPD))
                if "<<FILL-IN" in str(v)]
    if unfilled:
        print(f"CONFIG NOT FILLED: {unfilled} in dpd_states/config.py")
        return None

    # 1. load + schema guard ---------------------------------------------------------
    sdf = catalog.load(ds)
    required = [cfg.KEY, cfg.COL_DPD] + ([cfg.COL_SNAPSHOT] if cfg.COL_SNAPSHOT else [])
    missing = [c for c in required if c not in sdf.columns]
    if missing:
        print(f"SCHEMA MISMATCH in {ds}. missing={missing}")
        print(f"available={sorted(sdf.columns)}")
        return None
    optional = {**cfg.AXIS_COLS, **cfg.EXISTING_RULE_COLS, **cfg.FLAG_COLS}
    present = {name: col for name, col in optional.items() if col and col in sdf.columns}
    absent = {name: col for name, col in optional.items() if col and col not in sdf.columns}

    # 2. scope FIRST: filter, latest snapshot, normalise the string -------------------
    if cfg.ROW_FILTER:
        sdf = sdf.where(cfg.ROW_FILTER)
    if cfg.COL_SNAPSHOT:
        latest = sdf.agg(F.max(cfg.COL_SNAPSHOT)).first()[0]
        sdf = sdf.where(F.col(cfg.COL_SNAPSHOT) == F.lit(latest))
    s = F.col(cfg.COL_DPD).cast("string")
    if cfg.STRIP_CHARS:
        s = F.regexp_replace(s, "[" + re.escape(cfg.STRIP_CHARS) + "]", "")
    for a, b in (cfg.CHAR_MAP or {}).items():
        s = F.regexp_replace(s, re.escape(a), b)
    if not cfg.LEFTMOST_IS_CURRENT:
        s = F.reverse(s)
    sdf = sdf.select(F.col(cfg.KEY).alias("_key"), s.alias("dpd_string"),
                     *[F.col(c).alias(n) for n, c in present.items()])

    spine = [str(b) for b in cfg.SPINE_BUCKETS]
    is_cur = F.substring("dpd_string", 1, 1).isin(spine)
    is_bt = (F.length("dpd_string") > k) & F.substring("dpd_string", k + 1, 1).isin(spine)
    exited = is_bt & (F.substring("dpd_string", 1, 1).cast("int") >= cfg.EXIT_BUCKET)
    counts = sdf.agg(
        F.count("*").alias("rows"),
        F.countDistinct("_key").alias("accounts"),
        F.sum(is_cur.cast("int")).alias("current_spine"),
        F.sum(is_bt.cast("int")).alias("backtest_spine"),
        F.sum(exited.cast("int")).alias("backtest_now_8plus"),
        F.sum((~F.col("dpd_string").rlike("^[0-9]+$")).cast("int")).alias("non_digit_strings"),
        F.expr("percentile_approx(length(dpd_string), array(0.05, 0.5, 0.95))").alias("len_p05_p50_p95"),
    ).first().asDict()
    sdf = sdf.drop("_key")                      # keys never leave Spark

    scope_note = (f"{ds}" + (f" where {cfg.ROW_FILTER}" if cfg.ROW_FILTER else "")
                  + (f", latest {cfg.COL_SNAPSHOT}" if cfg.COL_SNAPSHOT else "")
                  + f"; today's spine = current digit in {spine}; backtest = digit {k + 1} in {spine}"
                  + f"; sampled to <= {sample_n:,} rows each")
    warnings = []
    if counts["rows"] != counts["accounts"]:
        warnings.append("more rows than accounts — set COL_SNAPSHOT or de-duplicate")
    if cfg.DS_STRINGS_HAS_EXITED and counts["backtest_spine"] and not counts["backtest_now_8plus"]:
        warnings.append("no backtest account is at 8+ today — the table looks survivor-only; "
                        "outcomes would be biased. Point DS_STRINGS at a table that keeps exited "
                        "accounts, or set DS_STRINGS_HAS_EXITED = False")

    if check_only:
        ex = [r.dpd_string[:36] for r in sdf.where(is_cur).select("dpd_string").limit(5).collect()]
        print("=== DPD_STATES CHECK START ===")
        print(f"model_id: {model_id}")
        print(f"scope: {scope_note}")
        print(f"counts: {counts}")
        print(f"optional columns present: {present}")
        print(f"optional columns configured but missing: {absent}")
        print(f"example strings (no keys, newest first, 36 months): {ex}")
        for w in warnings:
            print(f"WARNING: {w}")
        print("=== DPD_STATES CHECK END ===")
        return {"model_id": model_id, "counts": counts, "present": present, "absent": absent,
                "warnings": warnings}

    # 3. collect two small samples (no keys), analyse in pandas -----------------------
    cur_pd = _sample(sdf.where(is_cur), counts["current_spine"], sample_n, seed).toPandas()
    bt_pd = None
    if cfg.DS_STRINGS_HAS_EXITED and counts["backtest_spine"]:
        bt_pd = _sample(sdf.where(is_bt).select("dpd_string"), counts["backtest_spine"],
                        sample_n, seed).toPandas()
    R, report = run(cur_pd, bt_pd, cfg)
    checks = evaluate(R)

    payload = {
        "task": "DPD_STATES_VALIDATION",
        "run_date": datetime.date.today().isoformat(),
        "model_id": model_id,
        "scope": scope_note,
        "counts": counts,
        "warnings": warnings,
        "optional_columns_present": sorted(present),
        "results": R,
        "expectations": checks.to_dict("records"),
    }

    # 4. file hand-off + printed headline --------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", model_id).strip("_")
    stamp = payload["run_date"].replace("-", "")
    out = out_dir / f"dpd_states_validation_{slug}_{stamp}.json"
    out.write_text(json.dumps(payload, indent=2, default=str))
    rep = out.with_suffix(".md")
    rep.write_text(f"# DPD deterioration states — validation\n\nmodel_id: `{model_id}` · run "
                   f"{payload['run_date']} · scope: {scope_note}\n\n"
                   + "".join(f"> WARNING: {w}\n\n" for w in warnings)
                   + "## 0. Expectation checks\n\n" + md(checks, index=False) + "\n\n" + report + "\n")

    n_status = checks.status.value_counts().to_dict()
    rec = R["states_today"][RECOMMENDED]["share"]
    print("=== DPD_STATES OUTPUT START ===")
    print(f"model_id: {model_id}")
    print(f"scope: {scope_note}")
    print(f"counts: {counts}")
    for w in warnings:
        print(f"WARNING: {w}")
    print(f"expectations: {n_status}")
    for r in checks.itertuples():
        print(f"  {r.id:<4} {r.status:<7} observed={r.observed!s:<8} expected={r.expected:<8} {r.check[:70]}")
    print(f"{RECOMMENDED} shares today: " + ", ".join(f"{DISPLAY_NAMES[s]}={v:.1%}" for s, v in rec.items()))
    print(f"wrote: {out} and {rep.name} -> commit & push from PROD, pull in UAT")
    print("=== DPD_STATES OUTPUT END ===")
    return payload
