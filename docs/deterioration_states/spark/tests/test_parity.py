"""Parity: the per-account core of crx_persona/_dpd_journey.py vs the signed-off numpy
reference (docs/deterioration_states/dpd_states). No Spark needed.

    python docs/deterioration_states/spark/tests/test_parity.py        # or: pytest <this file>

Checks every feature and every state (options A/B/C, 180+ prototype) on the synthetic
generators, the business edge cases (selftest CASES / CROP_CASES) on CC and RL numbering,
and the Stage 1 gap rules.
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "crx_persona"))       # the engine
sys.path.insert(0, str(HERE.parents[2]))                       # the reference package

import _dpd_journey as J                                       # noqa: E402
from dpd_states import segment_180, synth                      # noqa: E402
from dpd_states.analysis import crop_history                   # noqa: E402
from dpd_states.config import MAX_HISTORY_MONTHS               # noqa: E402
from dpd_states.features import build_features                 # noqa: E402
from dpd_states.selftest import CASES, CROP_CASES              # noqa: E402
from dpd_states.states import OPTIONS, assign_states           # noqa: E402

N = 20_000
FEATURES = [k for k in J.journey_features([1, 2, 3, 4])]


def _chron(s: str) -> list[int]:
    """Bank string (leftmost = current) -> list oldest -> newest."""
    return [int(ch) for ch in reversed(s)]


def _to_rl(cc: list[int]) -> list[int]:
    """CC buckets -> RL native buckets (CC 0/1 -> 0, CC 2 -> 1, ..., CC 8/9 -> 7)."""
    return [min(max(x, 1), 8) - 1 for x in cc]


def _compare(ref, mine, what: str) -> int:
    bad = 0
    for k in FEATURES:
        r, m = ref[k], mine[k]
        same = abs(float(r) - float(m)) < 1e-9 if isinstance(m, float) else bool(r == m) if isinstance(m, bool) else int(r) == int(m)
        if not same:
            bad += 1
            if bad <= 3:
                print(f"  MISMATCH {what} {k}: reference {r!r} vs engine {m!r}")
    return bad


def _reference(strings, cropped):
    import pandas as pd
    f = build_features(pd.DataFrame({"dpd_string": list(strings), "history_truncated": list(cropped)}))
    return f, {o: assign_states(f, **OPTIONS[o]) for o in OPTIONS}


def test_spine_cc_and_rl():
    synth.calibrate(n=4000, iters=3)
    df = synth.generate(N)
    s, cropped = crop_history(df.dpd_string, MAX_HISTORY_MONTHS)
    f, ref_states = _reference(s, cropped)
    bad = 0
    for i, (string, cr) in enumerate(zip(s, cropped)):
        b = _chron(string)
        for o in OPTIONS:
            mine = J.classify(b, bool(cr), 0, 9, "60_180", o)
            if mine["det_state"] != ref_states[o].iloc[i]:
                bad += 1
                print(f"  STATE {o} {string}: {ref_states[o].iloc[i]} vs {mine['det_state']}")
        bad += _compare(f.iloc[i], mine, f"cc {string}")
    # RL: the same journeys in RL numbering must give the same states / features
    rl_ref_strings = ["".join(str(min(max(x, 1), 8)) for x in reversed(_chron(x))) for x in s]
    f_rl, ref_rl = _reference(rl_ref_strings, cropped)
    for i, (string, cr) in enumerate(zip(s, cropped)):
        mine = J.classify(_to_rl(_chron(string)), bool(cr), 1, 8, "60_180", "B_balanced_6")
        if mine["det_state"] != ref_rl["B_balanced_6"].iloc[i]:
            bad += 1
            print(f"  RL STATE {string}: {ref_rl['B_balanced_6'].iloc[i]} vs {mine['det_state']}")
        bad += _compare(f_rl.iloc[i], mine, f"rl {string}")
    print(f"spine: {len(s):,} accounts x {len(OPTIONS)} options + RL, {bad} mismatches")
    assert bad == 0


def test_segment_180_cc():
    df = segment_180.generate_180(8000, median_months_at_9=12)
    f = segment_180.features_180(df)
    ref = segment_180.assign_180(f)
    bad = 0
    for i, (string, cr) in enumerate(zip(f.dpd_string, f.history_truncated)):
        mine = J.classify(_chron(string), bool(cr), 0, 9, "180_plus", "B_balanced_6")
        if mine["det_state"] != ref.iloc[i]:
            bad += 1
            if bad <= 5:
                print(f"  180 STATE {string}: {ref.iloc[i]} vs {mine['det_state']}")
        for k in ("all_default", "months_in_default", "default_left_censored", "paid_in_default",
                  "stabilized_months_in_4_7"):
            if bool(f[k].iloc[i] == mine[k]) is False:
                bad += 1
        if int(f.pay_events_before_9.iloc[i]) != mine["pay_events_before_top"]:
            bad += 1
    print(f"180+: {len(f):,} accounts, {bad} mismatches")
    assert bad == 0


def test_business_cases():
    bad = 0
    for chron, want, why in CASES:
        b = [int(ch) for ch in chron.replace(" ", "")]
        for name, buckets, off, top in (("cc", b, 0, 9), ("rl", _to_rl(b), 1, 8)):
            got = J.classify(buckets, False, off, top, "60_180", "B_balanced_6")["det_state"]
            if got != want:
                bad += 1
                print(f"  CASE {name} {chron!r}: want {want}, got {got} — {why}")
    for chron, n, want, why in CROP_CASES:
        b = [int(ch) for ch in chron.replace(" ", "")]
        kept, cropped = b[-n:], len(b) >= n
        got = J.classify(kept, cropped, 0, 9, "60_180", "B_balanced_6")["det_state"]
        if got != want:
            bad += 1
            print(f"  CROP {chron!r}: want {want}, got {got} — {why}")
    # RL 180+: cap is RL 7 (canonical 8)
    rl180 = [
        ([0] * 20 + [1, 2, 3, 4, 5, 6, 7, 7, 7], "straight_roller_seasoned"),
        ([0] * 20 + [1, 2, 3, 4, 5, 6, 7, 7, 6, 7], "paying_in_default"),
        ([7, 7, 7, 7], "unknown"),
        ([0] * 20 + [1, 2, 3, 4, 5] + [6] * 12 + [7, 7], "broken_payer"),
        ([0] * 20 + [1, 2, 3, 4, 5, 6, 7] + [7] * 12, "straight_roller_seasoned"),   # 12 months at the cap: NOT stabilized
        ([0, 0, 1, 2, 3, 4, 5, 6, 7], "early_payment_default"),
    ]
    cc180 = [
        ([0] * 20 + [2, 3, 4, 5, 6, 7, 8, 9] + [9] * 12, "straight_roller_seasoned"),     # at the cap: NOT stabilized
        ([0] * 20 + [2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8], "stabilized"),                  # holding at 8 (below the cap)
        ([8, 9, 9, 9, 9, 9, 9], "unknown"),
    ]
    for buckets, want in cc180:
        got = J.classify(buckets, False, 0, 9, "180_plus", "B_balanced_6")["det_state"]
        if got != want:
            bad += 1
            print(f"  CC180 {buckets}: want {want}, got {got}")
    for buckets, want in rl180:
        got = J.classify(buckets, False, 1, 8, "180_plus", "B_balanced_6")["det_state"]
        if got != want:
            bad += 1
            print(f"  RL180 {buckets}: want {want}, got {got}")
    print(f"business cases: {len(CASES) * 2 + len(CROP_CASES) + len(rl180) + len(cc180)} checked, {bad} wrong")
    assert bad == 0


def test_build_history():
    """Stage 1 rules: dedupe, cycle shift, gap fill / roll / infer, truncate/drop, cropped."""
    def run(rows, first_raw=None, gmin=0, offset=0, fill=True, how="truncate", max_inf=2):
        first_raw = first_raw if first_raw is not None else min(r[0] for r in rows)
        return J.build_history(rows, first_raw, gmin, offset, fill, how, True, max_inf)

    bad = []
    r = run([(100, 1, 3), (101, 5, 4), (101, 9, 5), (102, 1, 5)])         # same month: latest wins
    bad += [] if r["buckets"] == [3, 5, 5] and r["n_dup_month_rows"] == 1 else ["dedupe latest"]
    r = run([(100, 1, 3), (101, 5, 4), (101, 5, 6), (102, 1, 6)])         # same day: worst wins
    bad += [] if r["buckets"] == [3, 6, 6] else ["dedupe tie"]
    r = run([(100, 1, 4), (102, 1, 4)])                                    # hold through
    bad += [] if r["buckets"] == [4, 4, 4] and r["n_gap_months_filled"] == 1 else ["hold fill"]
    r = run([(100, 1, 0), (102, 1, 1)])                                    # CC 0 _ 1: clean
    bad += [] if r["buckets"] == [0, 0, 1] and r["n_months_truncated"] == 0 else ["cc 0/1 fill"]
    r = run([(100, 1, 3), (103, 1, 6)])                                    # 3 _ _ 6: straight roll
    bad += [] if r["buckets"] == [3, 4, 5, 6] and r["n_gap_months_rolled"] == 2 else ["roll fill"]
    r = run([(100, 1, 0), (102, 1, 2)], offset=1)                          # RL 0 _ 2 -> 0 1 2
    bad += [] if r["buckets"] == [0, 1, 2] else ["rl roll fill"]
    r = run([(100, 1, 0), (101, 1, 0), (105, 1, 4), (106, 1, 5)])          # 0 _ _ _ 4: unresolvable
    bad += [] if (r["buckets"] == [4, 5] and r["n_months_truncated"] == 5
                  and r["history_cropped"] and r["legacy_drop"]) else ["truncate"]
    r = run([(100, 1, 3), (102, 1, 4)])                                    # 3 _ 4: inferred, roll late
    bad += [] if r["buckets"] == [3, 3, 4] and r["n_gap_months_inferred"] == 1 else ["infer up"]
    r = run([(100, 1, 6), (103, 1, 3)])                                    # 6 _ _ 3: carry, pay at end
    bad += [] if r["buckets"] == [6, 6, 6, 3] and r["n_gap_months_inferred"] == 2 else ["infer down"]
    r = run([(100, 1, 3), (102, 1, 4)], max_inf=0)                         # inference off -> truncate
    bad += [] if r["buckets"] == [4] and r["n_months_truncated"] == 2 else ["infer off"]
    # cycle shift: bills on day 30 of month 100 and day 31 / day 61 (next cycle) in month 101,
    # none in 102: the later bill of 101 belongs to 102
    r = run([(100, 30, 2), (101, 60, 3), (101, 61, 4), (103, 90, 5)])
    bad += [] if (r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1
                  and r["n_gap_months_filled"] + r["n_gap_months_inferred"] == 0) else ["cycle shift fwd"]
    r = run([(100, 1, 2), (102, 50, 3), (102, 80, 4), (103, 90, 5)])       # earlier bill moves back
    bad += [] if r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1 else ["cycle shift back"]
    r = run([(100, 1, 0), (102, 1, 4)], how="drop", max_inf=0)
    bad += [] if r["build_status"] == "dropped_unresolvable_gap" else ["drop"]
    r = run([(100, 1, 0), (101, 1, 2)], fill=False)
    bad += [] if r["history_cropped"] is False else ["not cropped"]
    r = run([(110, 1, 0), (111, 1, 2)], first_raw=90)                      # floor cut older rows
    bad += [] if r["history_cropped"] else ["cropped by floor"]
    r = run([(110, 1, 0), (111, 1, 2)], gmin=110)                          # starts with the source
    bad += [] if r["history_cropped"] else ["cropped at source start"]
    r = J.build_history([], 100, 0, 0)
    bad += [] if r["build_status"] == "no_rows_in_window" else ["empty"]
    print(f"build_history: {17 - len(bad)}/17 rules OK {bad or ''}")
    assert not bad


if __name__ == "__main__":
    fails = 0
    for t in (test_build_history, test_business_cases, test_segment_180_cc, test_spine_cc_and_rl):
        try:
            t()
        except AssertionError:
            fails += 1
            print(f"FAILED {t.__name__}")
    print("PARITY PASSED" if not fails else f"PARITY FAILED ({fails})")
    sys.exit(1 if fails else 0)
