"""End-to-end self-test of the REAL-DATA path on synthetic data (no Spark needed).

Builds the two frames the Spark snippet would collect — today's spine with optional
axis columns, and latest-month strings for the backtest — runs analysis.run and the
expectations, and writes the same report the workplace run produces.

    cd docs/deterioration_states && python -m dpd_states.selftest [n_accounts]

Pass = no FAIL and E01 (MECE) PASS. WARNs are reported, not asserted: synthetic data is
calibrated to the bank's figures but is not the bank's book.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from . import config, synth
from .analysis import md, run
from .expectations import evaluate
from .features import build_features
from .states import OPTIONS, RECOMMENDED, assign_states

OUT = Path(__file__).resolve().parents[1] / "validation"


def _fake_axes(cur, rng):
    """Plausible other-axis columns so the overlap code paths run. Not real behaviour."""
    f = build_features(cur)
    st = assign_states(f, **OPTIONS[RECOMMENDED])
    money = np.where(f.paid_any_3m, 2, rng.choice([0, 1], len(f), p=[0.8, 0.2]))
    clean = (f.n_prior_episodes == 0).astype(int)
    ptp = rng.choice([0, 1, 2], len(f), p=[0.5, 0.3, 0.2])
    out = cur.copy()
    out["cred_money_in_points"] = money
    out["cred_clean_point"] = clean
    out["cred_ptp_points"] = ptp
    out["credibility_score"] = money + clean + ptp
    out["ability_score"] = rng.normal(50, 15, len(f)).round(1)
    out["reachable_flag"] = rng.choice([0, 1], len(f), p=[0.3, 0.7])
    out["in_country_flag"] = rng.choice([0, 1], len(f), p=[0.15, 0.85])
    # the bank's own rules: ours, with a little disagreement
    out["existing_bust_out"] = ((st == "early_payment_default") ^ (rng.random(len(f)) < 0.005)).astype(int)
    out["existing_stabilized"] = ((f.last6_in_band >= 5) ^ (rng.random(len(f)) < 0.005)).astype(int)
    return out


def main(n: int = 20_000) -> int:
    rng = np.random.default_rng(3)
    synth.calibrate()
    cur = synth.generate(n)[["dpd_string"]]
    cur = _fake_axes(cur, rng)
    # a few strings with a non-digit code and padding, to exercise CHAR_MAP / STRIP_CHARS
    cur.loc[cur.index[:50], "dpd_string"] = " " + cur.dpd_string[:50].str.replace("0", "X", n=1)
    latest = synth.latest_month_strings(n, k=6, seed=11)[["dpd_string"]]

    cfg = SimpleNamespace(**{k: getattr(config, k) for k in dir(config) if k.isupper()})
    cfg.CHAR_MAP = {"X": "0"}
    R, report = run(cur, latest, cfg)
    checks = evaluate(R)

    OUT.mkdir(exist_ok=True)
    stamp = date.today().strftime("%Y%m%d")
    (OUT / f"selftest_results_{stamp}.json").write_text(json.dumps(R, indent=2, default=str))
    (OUT / f"selftest_report_{stamp}.md").write_text(
        f"# Self-test on synthetic data — {stamp}\n\nFake axis columns; real-data code path.\n\n"
        "## 0. Expectation checks\n\n" + md(checks, index=False) + "\n\n" + report + "\n")

    print(md(checks[["id", "status", "observed", "expected", "check"]], index=False))
    ok = (checks.status != "FAIL").all() and checks.set_index("id").loc["E01", "status"] == "PASS"
    print("\nSELFTEST", "PASSED" if ok else "FAILED", f"-> {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 20_000))
