"""PROD check — run by a person with PROD access, AFTER the pipelines have run.

    kedro run --pipeline=crx_cc_a4_deterioration      # and/or crx_rl_a4_deterioration

Then, in a Kedro notebook / `kedro ipython` session where `catalog` exists:

    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "spark"))
    from prod_check import report
    report(catalog)                       # CC and RL; report(catalog, products=("cc",)) for one

READ-ONLY. Prints AGGREGATES ONLY (counts and shares — no account ids, no DPD strings)
between === DPD_JOURNEY PROD CHECK START / END ===. Paste that block back for review.
Datasets read: crx_<p>_dpd_sequences and crx_<p>_a4_deterioration (the pipeline outputs).
"""
from pyspark.sql import functions as F

TARGET_COVERAGE = 0.999


def _pct(x, n):
    return f"{x:,} ({x / n:.2%})" if n else f"{x:,}"


def _product(catalog, p: str) -> list[str]:
    seq = catalog.load(f"crx_{p}_dpd_sequences")
    out = catalog.load(f"crx_{p}_a4_deterioration")
    lines = [f"## {p.upper()}"]

    # -- Node 1: every account in the history, with a build status ----------------------
    s = seq.agg(
        F.count("*").alias("accounts"),
        F.sum((F.col("build_status") == "ok").cast("int")).alias("ok"),
        F.sum(F.col("legacy_drop").cast("int")).alias("legacy_drop"),
        F.sum(F.col("history_cropped").cast("int")).alias("cropped"),
        F.sum((F.col("n_months_truncated") > 0).cast("int")).alias("truncated"),
        F.sum((F.col("n_cycle_shift_moves") > 0).cast("int")).alias("acc_cycle_shift"),
        F.sum((F.col("n_gap_months_filled") > 0).cast("int")).alias("acc_gap_filled"),
        F.sum((F.col("n_gap_months_rolled") > 0).cast("int")).alias("acc_gap_rolled"),
        F.sum((F.col("n_gap_months_inferred") > 0).cast("int")).alias("acc_gap_inferred"),
        F.sum((F.col("n_invalid_rows") > 0).cast("int")).alias("acc_invalid_rows"),
        F.min("first_month").alias("first_month"),
        F.max("last_month").alias("last_month"),
        F.expr("percentile_approx(history_months, array(0.05, 0.5, 0.95))").alias("history_months_p05_p50_p95"),
    ).first().asDict()
    n = s["accounts"]
    lines.append(f"sequences: {n:,} accounts, months {s['first_month']} .. {s['last_month']}, "
                 f"history months p05/p50/p95 {s['history_months_p05_p50_p95']}")
    lines.append("build_status: " + ", ".join(
        f"{r['build_status']} {_pct(r['count'], n)}"
        for r in seq.groupBy("build_status").count().orderBy(F.desc("count")).collect()))
    lines.append(f"old rule would have dropped: {_pct(s['legacy_drop'], n)}")
    lg = seq.where("legacy_drop").agg(
        F.count("*").alias("n"),
        F.sum((F.col("n_cycle_shift_moves") > 0).cast("int")).alias("cycle_shift"),
        F.sum((F.col("n_gap_months_rolled") > 0).cast("int")).alias("straight_roll"),
        F.sum((F.col("n_gap_months_inferred") > 0).cast("int")).alias("inferred"),
        F.sum((F.col("n_months_truncated") > 0).cast("int")).alias("truncated"),
        F.expr("percentile_approx(n_months_truncated, 0.5)").alias("median_months_truncated"),
    ).first().asDict()
    lines.append(f"  of those, now resolved by (an account can have several): {lg}")
    lines.append(f"cropped {_pct(s['cropped'], n)}; truncated at a gap {_pct(s['truncated'], n)}; "
                 f"accounts with cycle-shift repair {_pct(s['acc_cycle_shift'], n)}, gap filled "
                 f"{_pct(s['acc_gap_filled'], n)}, straight-roll fill {_pct(s['acc_gap_rolled'], n)}, "
                 f"inferred fill {_pct(s['acc_gap_inferred'], n)}, invalid bucket rows {_pct(s['acc_invalid_rows'], n)}")

    # -- Node 2: coverage and state shares ------------------------------------------------
    segs = [r["det_segment"] for r in out.select("det_segment").distinct().collect()]
    for seg in segs or ["(empty output)"]:
        o = out.where(F.col("det_segment") == seg)
        m = o.count()
        cur = [r["current_bucket"] for r in o.select("current_bucket").distinct().collect()]
        # accounts whose latest bucket is in this segment but that were NOT classified
        in_seg = seq.where(F.element_at("dlq_buckets", -1).isin(cur)) if cur else seq.limit(0)
        lost = in_seg.where(F.col("build_status") != "ok").count()
        cov = m / (m + lost) if (m + lost) else 0.0
        lines.append(f"### segment {seg} (current buckets {sorted(cur)}): {m:,} classified, "
                     f"{lost:,} in segment but not classified -> coverage {cov:.3%} "
                     f"[{'OK' if cov >= TARGET_COVERAGE else 'BELOW 99.9%'}]")
        lines.append("| state | accounts | share |")
        lines.append("|---|---|---|")
        for r in o.groupBy("det_state").count().orderBy(F.desc("count")).collect():
            lines.append(f"| {r['det_state']} | {r['count']:,} | {r['count'] / m:.1%} |")
        q = o.agg(
            F.avg(F.col("starts_delinquent").cast("double")).alias("starts_delinquent"),
            F.avg(F.col("history_cropped").cast("double")).alias("cropped"),
            F.avg((F.col("history_stale_months") > 1).cast("double")).alias("stale_over_1m"),
            F.avg(F.col("restructure_blind_spot_flag").cast("double")).alias("restructured"),
            F.avg((F.col("n_glitches") > 0).cast("double")).alias("glitch_fixed"),
            F.avg((F.col("n_jumps_repaired") > 0).cast("double")).alias("jump_repaired"),
        ).first().asDict()
        lines.append("shares: " + ", ".join(f"{k} {v:.1%}" for k, v in q.items() if v is not None))
        lines.append("state x starts_delinquent / cropped (shares within state):")
        for r in (o.groupBy("det_state").agg(
                F.avg(F.col("starts_delinquent").cast("double")).alias("sd"),
                F.avg(F.col("history_cropped").cast("double")).alias("cr"))
                .orderBy("det_state").collect()):
            lines.append(f"  {r['det_state']}: starts_delinquent {r['sd']:.1%}, cropped {r['cr']:.1%}")
    return lines


def report(catalog, products=("cc", "rl")) -> str:
    lines = ["=== DPD_JOURNEY PROD CHECK START ==="]
    for p in products:
        try:
            lines += _product(catalog, p)
        except Exception as exc:          # one product failing must not hide the other
            lines.append(f"## {p.upper()}: FAILED — {type(exc).__name__}: {str(exc)[:300]}")
    lines.append("=== DPD_JOURNEY PROD CHECK END ===")
    text = "\n".join(lines)
    print(text)
    return text
