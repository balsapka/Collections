"""What we expect to see on real data, as checkable rules.

Each expectation states the metric, the expected range, why we expect it (synthetic
validation or the bank's own figures), and what to do if it is not met. `evaluate(R)`
reads the results dict from analysis.run and returns one row per check with
PASS / WARN / FAIL / SKIPPED / INFO.

Severity: FAIL = the run itself is not trustworthy (fix config/data before reading
anything else). WARN = the run is fine but an assumption behind the design is off —
follow the 'if not met' action. INFO = reported, no expectation.
"""
from __future__ import annotations

import pandas as pd

from .states import FIXED_STATES, RECOMMENDED

ROLL_TARGET = {4: 0.70, 5: 0.80, 6: 0.90, 7: 0.95}


def _card(R, option):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    return pd.DataFrame(bt["scorecards"][option]).set_index("state" if "state" in bt["scorecards"][option][0] else "index")


def _share(R, option):
    return pd.Series(R["states_today"][option]["share"])


def _sweep(R, name):
    return pd.DataFrame(R["sweeps"][name])


def _eta(R, axis, option=RECOMMENDED):
    ov = R.get("overlap_other_axes", {})
    if "eta2_by_option" not in ov:
        return None
    eta = pd.DataFrame(ov["eta2_by_option"]).set_index("axis")
    return float(eta.loc[axis, option]) if axis in eta.index else None


def _agree(R, state, key):
    a = R.get("existing_rule_agreement")
    return a[state][key] if isinstance(a, dict) and state in a else None


def _hold_gap(R):
    c = _card(R, RECOMMENDED)
    if c is None or "holding" not in c.index:
        return None
    rolling = c.loc[[s for s in c.index if s in FIXED_STATES], "roll_next_month"]
    w = c.loc[rolling.index, "share"]
    return float((rolling * w).sum() / w.sum() - c.loc["holding", "roll_next_month"])


def _fixed_stability(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        return None
    return float(c.loc[[s for s in c.index if s in FIXED_STATES], "same_state_next_month"].min())


def _roll_dev(R):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    rr = {int(k): v for k, v in bt["monthly_roll_rate"].items()}
    return max(abs(rr.get(b, float("nan")) - t) for b, t in ROLL_TARGET.items())


def _resid_gain(R):
    rows = pd.DataFrame(R["residual_cluster_agreement"]).set_index("k")
    return float(rows.loc[6, f"agree_{RECOMMENDED}"] - rows.loc[6, "agree_A_minimal_4"])


def _runup_sharpness(R):
    sw = _sweep(R, "sudden_max_runup").set_index("sudden_max_runup")
    g3 = sw.loc[3, "gradual_share"]
    return float(sw.loc[4, "gradual_share"] / g3) if g3 else None


def _partial(R):
    sw = _sweep(R, "partial_payer_test").set_index("partial_min_paid_rate")
    if "stability_of_fixed_states" not in sw:
        return None
    r = sw.loc[0.5]
    return {"still_partial": r["still_partial_next_month"],
            "stability_drop": r["stability_of_fixed_states_without_q3"] - r["stability_of_fixed_states"]}


def _spread(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        return None
    x = c.loc[[s for s in c.index if s in FIXED_STATES], "exit_8plus_within_k"]
    return float(x.max() - x.min())


# id, title, metric(R), check(value)->bool, expected (text), severity, why, if not met
EXPECTATIONS = [
    ("E01", "Every account gets exactly one state (all options)",
     lambda R: all(v["mece"] for v in R["states_today"].values()), lambda v: v is True,
     "True", "FAIL", "The tree has a default branch, so it is MECE by construction.",
     "A code or data-type bug — stop and fix before reading anything else."),
    ("E02", "Share of DPD strings that cannot be parsed",
     lambda R: R["data_quality"]["share_invalid_strings"], lambda v: v <= 0.02,
     "<= 2%", "FAIL", "Strings should be digits once CHAR_MAP / STRIP_CHARS are set.",
     "Inspect the non-digit characters; extend CHAR_MAP or STRIP_CHARS in config.py."),
    ("E03", "Backtest monthly roll rates match the bank's 70/80/90/95% (max abs deviation)",
     _roll_dev, lambda v: v <= 0.07,
     "<= 7pp", "FAIL", "Confirms the string orientation and the backtest reconstruction are right.",
     "Check LEFTMOST_IS_CURRENT and that DS_STRINGS keeps accounts that left the spine "
     "(survivor-only data shows roll rates that are too low)."),
    ("E04", "Share of histories that start inside the current spell (no clean month seen)",
     lambda R: R["data_quality"]["share_left_censored"], lambda v: v <= 0.10,
     "<= 10%", "WARN", "Full history is available for everyone.",
     "Strings are truncated; bust-out (short history) will be over-assigned — cap the "
     "bust-out rule to accounts with full history or raise the threshold."),
    ("E05", "Share of accounts with an unrepaired +2 jump",
     lambda R: R["data_quality"]["share_jump_left"], lambda v: v <= 0.02,
     "<= 2%", "WARN", "Billing-cycle jumps are mostly next to a hold and get repaired.",
     "Look at examples; if a systematic code (e.g. 2-cycle buckets) exists, adjust the encoding."),
    ("E06", "Current bucket mix declines from 4 to 7",
     lambda R: R["data_quality"]["bucket_mix"].get(4, 0) - R["data_quality"]["bucket_mix"].get(7, 0),
     lambda v: v >= 0, ">= 0", "WARN", "Flow-driven book with rising roll rates (synthetic 29/26/23/22%).",
     "Check the spine filter and whether a cohort shock is passing through."),
    ("E07", "One spell only, spell counted from bucket 3",
     lambda R: R["data_quality"]["share_one_spell_from3"], lambda v: 0.78 <= v <= 0.92,
     "78–92%", "WARN", "Bank figure ~85% (synthetic 83%). If the 'from 4' figure is the one "
     "near 85%, the bank counts spells from 4.",
     "Set relapse_min_prior_peak to whichever spell definition matches the bank's 85%."),
    ("E08", "Bust-out share (today)",
     lambda R: _share(R, RECOMMENDED).get("bust_out", 0), lambda v: 0.04 <= v <= 0.08,
     "4–8%", "WARN", "Bank's own rule gives ~6% (synthetic 5.8%).",
     "Move bust_max_history along the sweep until the share matches the bank's rule."),
    ("E09", "Holding share (today)",
     lambda R: _share(R, RECOMMENDED).get("holding", 0), lambda v: 0.04 <= v <= 0.09,
     "4–9%", "WARN", "Bank's own stabilized rule gives ~6% (synthetic 6.6%).",
     "Compare with the bank's implementation of the 5-of-6 rule (E10/E11)."),
    ("E10", "Recall of the bank's existing bust-out flag",
     lambda R: _agree(R, "bust_out", "recall_of_theirs"), lambda v: v >= 0.80,
     ">= 80%", "WARN", "Same concept; thresholds may differ slightly.",
     "Read the bank's rule and align bust_max_history / the prior-peak guard."),
    ("E11", "Recall of the bank's existing stabilized flag",
     lambda R: _agree(R, "holding", "recall_of_theirs"), lambda v: v >= 0.90,
     ">= 90%", "WARN", "Holding IS the bank's 5-of-6 rule; only bust-out-first ordering differs.",
     "Check the band definition (±1 of today's bucket, 5 of last 6 months incl. today)."),
    ("E12", "Holding separates risk: weighted next-month roll of fixed states minus holding",
     _hold_gap, lambda v: v >= 0.20,
     ">= 20pp", "WARN", "Synthetic: holding 44% vs ~85% for the rest.",
     "Holding is not behaving as 'stable'; check payment holidays / restructuring flags (E21) "
     "and try hold_min_in_band = 6."),
    ("E13", "Fixed states keep their state next month (minimum over fixed states)",
     _fixed_stability, lambda v: v >= 0.95,
     ">= 95%", "WARN", "Run-up and history are fixed once past 4 (synthetic 98–100%).",
     "A feature is drifting with time since 4 — inspect which state leaks and why."),
    ("E14", "Holding persistence next month",
     lambda R: (_card(R, RECOMMENDED).loc["holding", "same_state_next_month"]
                if _card(R, RECOMMENDED) is not None else None),
     lambda v: 0.45 <= v <= 0.85, "45–85%", "WARN",
     "Holding is current behaviour; it should persist but not forever (synthetic 60%).",
     "Too low: the band is too loose. Too high: frozen buckets (holidays) are being read as payments."),
    ("E15", "Option A: sudden share",
     lambda R: _share(R, "A_minimal_4").get("sudden_decline", 0), lambda v: 0.55 <= v <= 0.80,
     "55–80%", "WARN", "Most accounts roll straight 2-3-4 (synthetic 70%).",
     "If much lower, many run-ups contain a hold — check +2/billing artefacts before trusting gradual."),
    ("E16", "Every option-B state holds at least 5% of the spine",
     lambda R: float(_share(R, "B_balanced_6").min()), lambda v: v >= 0.05,
     ">= 5%", "WARN", "Synthetic minimum 5.8% (bust-out).",
     "Merge the small state into its neighbour (relapse→sudden, early_life→established)."),
    ("E17", "Option C: smaller of gradual_slide / gradual_fought_back",
     lambda R: float(_share(R, "C_detailed_7").reindex(["gradual_slide", "gradual_fought_back"]).fillna(0).min()),
     lambda v: v >= 0.04, ">= 4%", "WARN", "Synthetic 10% / 6%.",
     "Too small to act on — use option B."),
    ("E18", "Holding sits low in the spine: share at bucket 4 / share at bucket 7",
     lambda R: (R["states_today"][RECOMMENDED]["by_bucket"].get(4, {}).get("holding", 0)
                / max(R["states_today"][RECOMMENDED]["by_bucket"].get(7, {}).get("holding", 0), 1e-9)),
     lambda v: v >= 2, ">= 2x", "WARN", "90–95% roll rates at 6–7 leave little room to hold there.",
     "Holders at 6–7 are unusual — check for frozen buckets (payment holidays)."),
    ("E19", "Orthogonality: credibility score explained by the states (eta²)",
     lambda R: _eta(R, "credibility_score"), lambda v: v <= 0.25,
     "<= 0.25", "WARN", "Known overlap via holding (money in) and relapse (clean point), but "
     "the states should not reproduce the score.",
     "Use option A (drops relapse) or report holding under credibility instead."),
    ("E19b", "Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²)",
     lambda R: _eta(R, "cred_clean_point"), lambda v: v <= 0.50,
     "<= 0.50", "WARN", "Relapse is defined from earlier spells — the same history the clean point "
     "scores. Synthetic (with a clean point = 'no earlier spell'): 0.84 → WARN.",
     "Relapse duplicates the credibility clean point: use option A, or keep relapse and "
     "tell the persona grid it is the same signal (it is only 1 of credibility's 5 points)."),
    ("E20", "Orthogonality: ability score explained by the states (eta²)",
     lambda R: _eta(R, "ability_score"), lambda v: v <= 0.10,
     "<= 0.10", "WARN", "DPD shape should carry little of salary/inflow/CASA.",
     "Sudden vs gradual may be a proxy for income loss — fine, but say so in the persona grid."),
    ("E21", "Holders with money coming in (credibility component or DPD proxy)",
     lambda R: R["overlap_other_axes"]["holding_vs_money_in"]["holders_with_money_in"],
     lambda v: v >= 0.90, ">= 90%", "WARN",
     "Holding = paid one month's due most months, so money must be coming in (synthetic 100%).",
     "Holders without money in are frozen buckets (holiday/restructure) — exclude those months."),
    ("E22", "Residual clusters agree more with option B than with A (ARI gain at k=6)",
     _resid_gain, lambda v: v >= 0.15, ">= 0.15", "WARN",
     "Synthetic: 0.55 (B) vs 0.16 (A) — the data has more than two residual groups.",
     "The extra B splits are not natural groups in this book — prefer option A."),
    ("E23", "One paid month on the way down matters: gradual share at run-up<=4 / at <=3",
     _runup_sharpness, lambda v: v <= 0.70, "<= 0.70", "WARN",
     "Synthetic 0.56: most gradual accounts held exactly once.",
     "Gradual is driven by long run-ups, not single payments — keep 3 but review examples."),
    ("E24", "Partial payer stays rejected: share still partial next month at 0.5",
     lambda R: (_partial(R) or {}).get("still_partial"), lambda v: v <= 0.75, "<= 75%", "WARN",
     "Synthetic 63%: unstable current-behaviour state.",
     "If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'."),
    ("E25", "INFO — spread of exit-within-k across fixed states (option B)",
     _spread, None, "report", "INFO",
     "Synthetic data cannot show this (same post-4 dynamics by construction).",
     ">= 5pp means the mechanism carries risk information beyond holding."),
]


def evaluate(R: dict) -> pd.DataFrame:
    rows = []
    for eid, title, metric, check, expected, sev, why, action in EXPECTATIONS:
        try:
            v = metric(R)
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, ZeroDivisionError):
            v = None
        if v is None or (isinstance(v, float) and v != v):
            status = "SKIPPED"
        elif check is None:
            status = "INFO"
        else:
            status = "PASS" if check(v) else sev
        rows.append({"id": eid, "status": status, "check": title,
                     "observed": round(v, 3) if isinstance(v, float) else v,
                     "expected": expected, "why": why, "if_not_met": action})
    return pd.DataFrame(rows)
