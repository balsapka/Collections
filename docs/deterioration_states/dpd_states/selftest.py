"""End-to-end self-test of the REAL-DATA path on synthetic data (no Spark needed).

Builds the two frames the Spark snippet would collect — today's spine with optional
axis columns, and latest-month strings for the backtest — runs analysis.run and the
expectations, and writes the same report the workplace run produces.

    python docs/deterioration_states/run.py selftest [n_accounts]       # from any folder

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

# Edge cases discussed with the business owner, written OLDEST -> NEWEST (the last digit is
# today's bucket), with the option-B state they must get. Any rule change that moves one
# of these fails the self-test.
CASES = [
    ("0 2 0 2 3 4", "early_payment_default", "3 months incl. one blip, then straight roll"),
    ("0 0 0 2 3 4", "early_payment_default", "3 clean months, straight roll"),
    ("0 2 3 4 5", "early_payment_default", "1 clean month"),
    ("0 0 2 0 2 3 4", "straight_roller_early_life", "4 months of history: too long for EPD"),
    ("0 0 0 0 0 0 2 3 4", "straight_roller_early_life", "6 clean months: early-life default, not EPD"),
    ("0 2 0 2 0 2 3 4", "straight_roller_early_life", "two blips: not EPD"),
    ("0 2 3 4 0 0 2 3 4 5 6", "repeat_delinquent", "paid off from 4, then relapsed"),
    ("0 0 2 2 3 4", "slow_roller", "held once on the way down"),
    ("0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4 5", "stabilized", "staircase holding at 4 then one step"),
    ("000000000000002345", "straight_roller_seasoned", "14 clean months, straight roll"),
    ("0000000000000234444567", "straight_roller_seasoned", "held at 4, then rolled 3 buckets: not stable"),
    ("0000000000000023455555", "stabilized", "holding at 5"),
    ("00000000234443345433456554", "stabilized", "oscillating payer (example 1)"),
    ("00000000234443345433456654", "stabilized", "oscillating payer that just paid down 6-5-4 (example 2)"),
    ("0 0 2 3 4 4 4 4 4 4", "stabilized", "entered like EPD but pays the monthly due since: not EPD"),
    ("0 0 2 3 4 4 5 6", "straight_roller_early_life", "entered like EPD, paid once at 4: EPD needs no payment"),
    ("4 5 6 7", "history_starts_delinquent", "string starts delinquent (restructured / missing history)"),
    ("0000000000000000224", "straight_roller_seasoned", "+2 jump after a hold at 2: repaired to 2 3 4"),
    ("00000000000000002244", "straight_roller_seasoned", "same account a month later: fixed state must not change"),
    ("000034", "straight_roller_early_life", "jump from clean to 3: no clean month is borrowed"),
    ("0 2 3 4" + " 0" * 20 + " 2 3 4", "straight_roller_seasoned", "cured 20 months earlier: outside 12-month window"),
    ("0 2 3 4" + " 0" * 8 + " 2 3 4 5", "repeat_delinquent", "cured 8 months earlier: repeat delinquent"),
    ("0000000000000000 2 3 4 4 0 4 5", "stabilized", "single 0 inside a spell at 4 is a glitch, not a cure"),
    ("0000 3 0000000000000 2 3 4", "straight_roller_seasoned", "single spike 0 3 0 is a glitch, not an earlier spell"),
]


CROP_CASES = [   # (oldest -> newest, max months kept, expected option-B state, why)
    ("0" * 10 + "234" + "45" * 18 + "4", 32, "stabilized",
     "spell older than the window: not a data-quality case; long-run holder -> stabilized"),
    ("0" * 40 + "234", 32, "straight_roller_seasoned", "long clean history cropped: still seasoned"),
    ("0000000000234", 6, "straight_roller_seasoned", "cropped to 0 0 0 2 3 4: looks like EPD, but older than the window"),
    ("0 0 0 2 3 4", 32, "early_payment_default", "short history, not cropped: EPD"),
]


def check_crop() -> tuple[list[str], int]:
    import pandas as pd
    from .analysis import crop_history
    lines, bad = [], 0
    for chron, n, want, why in CROP_CASES:
        s, tr = crop_history(pd.Series([chron.replace(" ", "")[::-1]]), n)
        f = build_features(pd.DataFrame({"dpd_string": s, "history_truncated": tr}))
        got = assign_states(f, **OPTIONS[RECOMMENDED]).iloc[0]
        bad += got != want
        lines.append(f"{'OK  ' if got == want else 'FAIL'} keep {n:>2}: {chron[-24:]:<25} -> {got:<27} {why}")
    return lines, bad


def check_file_mode() -> bool:
    """File mode end to end on a temporary CSV (no openpyxl needed): reading the text column,
    filtering to today's spine, survivor-only checks, results written outside the repo."""
    import contextlib
    import io
    import tempfile
    from . import config, file_mode
    df = synth.generate(1500, seed=21)[["dpd_string"]].rename(columns={"dpd_string": config.COL_DPD})
    df.loc[df.index[:100], config.COL_DPD] = "3" + df[config.COL_DPD][:100].str[1:]   # outside the spine
    df["derived_column"] = 1
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "mock.csv"
        df.to_csv(src, index=False)
        with contextlib.redirect_stdout(io.StringIO()):
            payload = file_mode.main(str(src), out_dir=tmp)
    good = (payload["counts"]["current_spine"] == 1400
            and payload["results"]["states_today"][RECOMMENDED]["mece"]
            and isinstance(payload["results"].get("survivor_checks"), dict))
    print(f"\nFile mode on a temporary CSV: {'OK' if good else 'FAIL'} "
          f"(spine {payload['counts']['current_spine']} of {payload['counts']['rows']} rows)")
    return good


def check_cases() -> list[str]:
    import pandas as pd
    df = pd.DataFrame({"dpd_string": [c.replace(" ", "")[::-1] for c, _, _ in CASES]})
    got = assign_states(build_features(df), **OPTIONS[RECOMMENDED])
    lines, bad = [], 0
    for (c, want, why), g in zip(CASES, got):
        ok = g == want
        bad += not ok
        lines.append(f"{'OK  ' if ok else 'FAIL'} {c[:36]:<37} -> {g:<27} {'' if ok else '(expected ' + want + ') '}{why}")
    return lines, bad


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
    case_lines, bad = check_cases()
    crop_lines, bad_crop = check_crop()
    print("\nReliable-window cropping:\n" + "\n".join(crop_lines))
    bad += bad_crop
    file_ok = check_file_mode()
    print("\nEdge cases (oldest -> newest, option B):\n" + "\n".join(case_lines))
    (OUT / f"selftest_report_{stamp}.md").write_text(
        (OUT / f"selftest_report_{stamp}.md").read_text().replace(
            "## 0. Expectation checks", "## 0a. Edge cases (oldest → newest, option B)\n\n```\n"
            + "\n".join(case_lines) + "\n```\n\n## 0. Expectation checks"))
    ok = ((checks.status != "FAIL").all() and checks.set_index("id").loc["E01", "status"] == "PASS"
          and bad == 0 and file_ok)
    print("\nSELFTEST", "PASSED" if ok else "FAILED", f"-> {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 20_000))
