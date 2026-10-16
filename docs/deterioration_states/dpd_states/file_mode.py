"""Validate the states on a DPD-history FILE (xlsx / csv / parquet) — no Spark needed.

    python docs/deterioration_states/run.py validate                              # cfg.INPUT_FILE
    python docs/deterioration_states/run.py validate data/input/other_file.xlsx   # another file

Reads cfg.COL_DPD (leftmost = most recent month) as TEXT, keeps today's spine (current
bucket in cfg.SPINE_BUCKETS), runs analysis.run + the expectations, and writes
results/dpd_states_file_<file>_<date>.json + .md (aggregates only, no keys, no raw strings).

A snapshot of today's segment has no outcomes: accounts that rolled to 8+ since are not
in it, so roll rates / exits are SKIPPED. Stability checks run on the survivors.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re

import pandas as pd

from . import config as cfg
from .analysis import md, run
from .expectations import evaluate
from .states import DISPLAY_NAMES, RECOMMENDED


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "conf").is_dir():
            return parent
    return here.parents[3]


def _read(path: pathlib.Path, col: str) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm", ".xls"):
        try:
            return pd.read_excel(path, dtype={col: str})
        except ImportError as e:                       # openpyxl missing
            raise SystemExit(f"{e}\nInstall it with: python -m pip install openpyxl") from None
    if suffix == ".csv":
        return pd.read_csv(path, dtype={col: str})
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise SystemExit(f"unsupported file type {suffix!r} — use .xlsx, .csv or .parquet")


def main(path: str | None = None, sample_n: int = 100_000, out_dir: str | None = None, seed: int = 42) -> dict:
    root = _repo_root()
    src = pathlib.Path(path) if path else pathlib.Path(cfg.INPUT_FILE)
    if not src.is_absolute() and not src.exists():
        src = root / src
    if not src.exists():
        raise SystemExit(f"input file not found: {src}")
    col = cfg.COL_DPD
    df = _read(src, col)
    if col not in df.columns:
        raise SystemExit(f"column {col!r} not in {src.name}. Available: {sorted(map(str, df.columns))}\n"
                         "Set COL_DPD in dpd_states/config.py.")

    s = df[col].astype("string")
    looks_numeric = s.str.contains(r"[.eE+]", regex=True, na=False).mean()
    if looks_numeric > 0.01:
        raise SystemExit(f"{looks_numeric:.0%} of {col} look like numbers (e.g. '5.4e+10'): the column was "
                         "stored as a number, which drops digits. Re-export it as text.")

    keep = {"dpd_string": s}
    optional = {**cfg.AXIS_COLS, **cfg.EXISTING_RULE_COLS, **cfg.FLAG_COLS}
    present = {name: c for name, c in optional.items() if c and c in df.columns}
    for name, c in present.items():
        keep[name] = df[c]
    cur = pd.DataFrame(keep).dropna(subset=["dpd_string"])
    cur["dpd_string"] = cur.dpd_string.astype(str)

    lead = cur.dpd_string.str.strip(cfg.STRIP_CHARS or None).str[:1]
    in_spine = lead.isin([str(b) for b in cfg.SPINE_BUCKETS])
    counts = {"rows": int(len(df)), "rows_with_string": int(len(cur)),
              "current_spine": int(in_spine.sum()),
              "non_digit_strings": int((~cur.dpd_string.str.strip(cfg.STRIP_CHARS or None)
                                        .str.fullmatch(r"\d+").fillna(False)).sum())}
    cur = cur[in_spine]
    if len(cur) > sample_n:
        cur = cur.sample(sample_n, random_state=seed)

    R, report = run(cur.reset_index(drop=True), None, cfg, spark_counts=counts)
    checks = evaluate(R)

    stamp = datetime.date.today().strftime("%Y%m%d")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", src.stem).strip("_")
    out = pathlib.Path(out_dir) if out_dir else pathlib.Path(__file__).resolve().parents[1] / "results"
    out.mkdir(parents=True, exist_ok=True)
    scope = (f"file {src.name}, column {col}; today's spine = leftmost digit in "
             f"{list(cfg.SPINE_BUCKETS)}; sampled to <= {sample_n:,}")
    payload = {"task": "DPD_STATES_VALIDATION_FILE", "run_date": datetime.date.today().isoformat(),
               "source": src.name, "scope": scope, "counts": counts,
               "optional_columns_present": sorted(present), "results": R,
               "expectations": checks.to_dict("records")}
    jf = out / f"dpd_states_file_{slug}_{stamp}.json"
    jf.write_text(json.dumps(payload, indent=2, default=str))
    mf = jf.with_suffix(".md")
    mf.write_text(f"# DPD deterioration states — validation on {src.name}\n\nRun {payload['run_date']} · "
                  f"{scope}\n\n## 0. Expectation checks\n\n" + md(checks, index=False) + "\n\n" + report + "\n")

    rec = R["states_today"][RECOMMENDED]["share"]
    print("=== DPD_STATES OUTPUT START ===")
    print(f"source: {src.name}")
    print(f"scope: {scope}")
    print(f"counts: {counts}")
    print(f"expectations: {checks.status.value_counts().to_dict()}")
    for r in checks.itertuples():
        print(f"  {r.id:<4} {r.status:<7} observed={r.observed!s:<14} expected={r.expected:<8} {r.check[:70]}")
    print(f"{RECOMMENDED} shares today: " + ", ".join(f"{DISPLAY_NAMES[k]}={v:.1%}" for k, v in rec.items()))
    print(f"wrote: {jf} and {mf.name}")
    print("=== DPD_STATES OUTPUT END ===")
    return payload
