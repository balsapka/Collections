"""What we expect to see on real data, as checkable rules.

Each expectation states the metric, the expected range, what the range is anchored on,
why we expect it, and what to do if it is not met. `evaluate(R)` reads the results dict
from analysis.run (in memory or re-loaded from the saved JSON — same answer) and returns
one row per check with PASS / WARN / FAIL / SKIPPED / INFO.

Severity: FAIL = the run itself is not trustworthy (fix config/data before reading
anything else). WARN = the run is fine but an assumption behind the design is off —
follow the 'if not met' action. INFO = reported, no pass/fail.

Anchor: bank = the bank's own figures or rules · design = follows from the rules by
construction · synthetic = calibrated on the synthetic generator only (a WARN there is a
prompt to look, not proof of a problem) · data = data-quality expectation.

Actions never say "tune a [business] parameter until the check passes": business
definitions change only with the business owner (escalate).
"""
from __future__ import annotations

import pandas as pd

from .states import FIXED_STATES, RECOMMENDED, option_states

ROLL_TARGET = {4: 0.70, 5: 0.80, 6: 0.90, 7: 0.95}
MIN_N = 100                    # states smaller than this are not used in stability checks


def _card(R, option):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    rows = bt["scorecards"][option]
    return pd.DataFrame(rows).set_index("state" if "state" in rows[0] else "index") if rows else None


def _share(R, option):
    allowed = [s for s in option_states(option) if s != "history_starts_delinquent"]
    return pd.Series(R["states_today"][option]["share"]).reindex(allowed).fillna(0.0)


def _sweep(R, name):
    return pd.DataFrame(R["sweeps"][name])


def _eta(R, axis, option=RECOMMENDED):
    ov = R.get("overlap_other_axes", {})
    if "eta2_by_option" not in ov:
        return None
    eta = pd.DataFrame(ov["eta2_by_option"]).set_index("axis")
    return float(eta.loc[axis, option]) if axis in eta.index and eta.loc[axis, option] is not None else None


def _agree(R, state, key):
    a = R.get("existing_rule_agreement")
    return a[state].get(key) if isinstance(a, dict) and state in a else None


def _bucket(d, b):
    return d.get(str(b), d.get(b))


def _stab_gap(R):
    c = _card(R, RECOMMENDED)
    if c is None or "stabilized" not in c.index:
        return None
    col = "roll_next_month_bucket_std"
    rolling = c.loc[[s for s in c.index if s in FIXED_STATES or s == "early_payment_default"], col].dropna()
    w = c.loc[rolling.index, "share"]
    return float((rolling * w).sum() / w.sum() - c.loc["stabilized", col])


def _surv_card(R):
    sc = R.get("survivor_checks", {})
    rows = sc.get("same_state_next_month")
    return pd.DataFrame(rows).set_index("state") if rows else None


def _fixed_stability(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        c = _surv_card(R)                 # snapshot-only run: survivors in the spine both months
    if c is None:
        return None
    c = c[(c.index.isin(FIXED_STATES)) & (c.n >= MIN_N)]
    return float(c.kept_or_stabilized_next_month.min()) if len(c) else None


def _stab_persist(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        c = _surv_card(R)
    return float(c.loc["stabilized", "same_state_next_month"]) if c is not None and "stabilized" in c.index else None


def _flips(R):
    bt = R.get("backtest")
    fl = bt.get("stabilized_flips") if isinstance(bt, dict) else R.get("survivor_checks", {}).get("stabilized_flips")
    return (fl or {}).get("with_long_run_clause", {}).get("bounce_back_share_of_ever_stabilized")


def _roll_dev(R):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    rr = bt["monthly_roll_rate"]
    return max(abs((_bucket(rr, b) if _bucket(rr, b) is not None else float("nan")) - t)
               for b, t in ROLL_TARGET.items())


def _invalid(R):
    dq = R["data_quality"]
    vals = [dq.get("share_invalid_strings_current"), dq.get("share_invalid_strings_backtest"),
            dq.get("share_non_digit_strings_table")]
    vals = [v for v in vals if v is not None]
    return max(vals) if vals else None


def _spell_closest(R):
    one = R["data_quality"]["one_spell_share"]
    name = min(one, key=lambda kk: abs(one[kk] - 0.85))
    return f"{name}: {one[name]:.2f}"


def _resid_gain(R):
    rows = R.get("residual_cluster_agreement")
    if not isinstance(rows, list):
        return None
    rows = pd.DataFrame(rows).set_index("k")
    return float(rows.loc[6, f"agree_{RECOMMENDED}"] - rows.loc[6, "agree_A_minimal_4"])


def _one_hold(R):
    bt = R.get("backtest")
    if not isinstance(bt, dict) or "one_hold_slow_rollers" not in bt:
        return None
    t = pd.DataFrame(bt["one_hold_slow_rollers"]).set_index("index")
    a = t.loc["slow roller: exactly one hold", "roll_next_month_bucket_std"]
    b = t.loc["straight roller", "roll_next_month_bucket_std"]
    return float(b - a)


def _partial(R):
    sw = _sweep(R, "paying_since_4_test").set_index("paying_since_4_min_rate")
    if "stability_of_fixed_states" not in sw or 0.5 not in sw.index:
        return None
    return sw.loc[0.5, "still_paying_since_4_next_month"]


def _spread(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        return None
    x = c.loc[[s for s in c.index if s in FIXED_STATES and s != "history_starts_delinquent"],
              "exit_8plus_within_3m_bucket_std"].dropna()
    return float(x.max() - x.min()) if len(x) > 1 else None


def _by_bucket_ratio(R):
    bb = R["states_today"][RECOMMENDED]["by_bucket"]
    at4 = (_bucket(bb, 4) or {}).get("stabilized", 0)
    at7 = (_bucket(bb, 7) or {}).get("stabilized", 0)
    return at4 / max(at7, 1e-9)


def _bucket_mix_drop(R):
    mix = R["data_quality"]["bucket_mix"]
    return (_bucket(mix, 4) or 0) - (_bucket(mix, 7) or 0)


def _max_eta(R, axes):
    vals = [v for v in (_eta(R, a) for a in axes) if v is not None]
    return max(vals) if vals else None


# id, title, metric(R), check(value)->bool, expected, severity, anchor, why, if not met
EXPECTATIONS = [
    ("E01", "Every account gets exactly one known state (all options)",
     lambda R: all(v["mece"] and v["n_unknown_state"] == 0 for v in R["states_today"].values()),
     lambda v: v is True, "True", "FAIL", "design",
     "The tree ends in a default branch, so it is MECE by construction; unknown labels mean a code change broke it.",
     "A code or data-type bug — stop and fix before reading anything else."),
    ("E02", "Unparseable strings (worst of: today's spine, backtest, whole table)",
     _invalid, lambda v: v <= 0.02, "<= 2%", "FAIL", "data",
     "Strings should be digits once CHAR_MAP / STRIP_CHARS are set.",
     "Inspect the non-digit characters (check-only output); extend CHAR_MAP (e.g. a write-off letter "
     "-> 9). Untreated letters silently drop accounts from the backtest."),
    ("E03", "Backtest monthly roll rates vs the bank's 70/80/90/95% (max abs deviation)",
     _roll_dev, lambda v: v <= 0.07, "<= 7pp", "FAIL", "bank",
     "Confirms the string orientation and that the one-table backtest is valid.",
     "Check, in order: LEFTMOST_IS_CURRENT; that every string ends in the SAME month (strings frozen at "
     "charge-off/closure, or exited accounts dropped from the table, make roll rates too low — set "
     "COL_STRING_AS_OF); letter exit codes missing from CHAR_MAP; whether the bank's roll rates are "
     "count- or balance-weighted."),
    ("E04", "Histories that start already delinquent (history_starts_delinquent)",
     lambda R: R["data_quality"]["share_history_starts_delinquent"], lambda v: v <= 0.01,
     "<= 1%", "WARN", "bank",
     "The first digit is the first billed month (0/1); exceptions are rare data issues and restructured "
     "accounts re-opened at their old bucket.",
     "Confirm the string-start convention (PROMPTS P1). Many cases point to restructured accounts or "
     "truncated strings — their treatment is a deferred business decision."),
    ("E05", "Accounts with an unrepaired +2 jump",
     lambda R: R["data_quality"]["share_jump_left"], lambda v: v <= 0.02,
     "<= 2%", "WARN", "synthetic",
     "Billing-cycle jumps mostly sit next to a hold and get repaired.",
     "Look at the shapes; a systematic code (e.g. 2-cycle buckets) needs an encoding change."),
    ("E06", "Current bucket mix declines from 4 to 7 (share at 4 minus share at 7)",
     _bucket_mix_drop, lambda v: v >= 0, ">= 0", "WARN", "bank",
     "Rising roll rates 70→95% thin the spine out towards bucket 7.",
     "Check the spine filter and whether a cohort shock is passing through."),
    ("E07", "INFO — one-spell share: definition closest to the bank's ~85%",
     _spell_closest, None, "report", "INFO", "bank",
     "Four spell definitions are reported in section 1; the bank's exact one is unconfirmed.",
     "Get the bank's definition; if it is 'reached 4' or 'run at >=4', discuss repeat_min_prior_peak."),
    ("E08", "Early payment default share (today)",
     lambda R: float(_share(R, RECOMMENDED).get("early_payment_default", 0)), lambda v: 0.03 <= v <= 0.08,
     "3–8%", "WARN", "bank",
     "Bank's own bust-out rule gives ~6%; the agreed definition is stricter (never paid since crossing 2).",
     "Compare with the bank's rule (E10, PROMPTS P4) and escalate to the business owner. Do not move "
     "epd_max_history to match a share."),
    ("E09", "Stabilized share (today)",
     lambda R: float(_share(R, RECOMMENDED).get("stabilized", 0)), lambda v: 0.04 <= v <= 0.10,
     "4–10%", "WARN", "bank",
     "Bank's 5-of-6 rule gives ~6%; the long-run clause adds about one point.",
     "Compare with the bank's implementation (E11, PROMPTS P4) and escalate."),
    ("E10", "Recall of the bank's existing bust-out flag by our EPD",
     lambda R: _agree(R, "early_payment_default", "recall_of_theirs"), lambda v: v >= 0.80,
     ">= 80%", "WARN", "bank",
     "Same concept; ours additionally requires no payment since crossing bucket 2.",
     "Read the bank's rule (PROMPTS P4), list the differences and escalate."),
    ("E11", "Recall of the bank's existing stabilized flag by our stabilized",
     lambda R: _agree(R, "stabilized", "recall_of_theirs"), lambda v: v >= 0.90,
     ">= 90%", "WARN", "bank",
     "Ours is the bank's 5-of-6 rule plus the long-run clause; differences: EPD/ordering, glitch and "
     "+2-jump cleaning.",
     "Check the band definition (±1 of today's bucket, 5 of the last 6 months incl. today)."),
    ("E12", "Stabilized separates risk: fixed states' next-month roll minus stabilized (bucket-standardised)",
     _stab_gap, lambda v: v >= 0.20, ">= 20pp", "WARN", "synthetic",
     "Synthetic: ~0.37. Standardised to the same bucket mix, because stabilized sits mostly at bucket 4.",
     "Stabilized is not behaving as stable: check payment holidays / restructuring flags (E21) and "
     "escalate whether to use 6 of 6."),
    ("E13", f"Fixed states keep their state (or move into stabilized) next month — min over states with n >= {MIN_N}",
     _fixed_stability, lambda v: v >= 0.95, ">= 95%", "WARN", "design",
     "Run-up, history and the repairs are causal: how they fell in never changes once past 4. EPD is "
     "not fixed (it ends when the account pays) and moving into stabilized is not a leak.",
     "A feature is drifting with time or with the next month's data — find the leaking state."),
    ("E14", "Stabilized persistence next month",
     _stab_persist,
     lambda v: 0.45 <= v <= 0.85, "45–85%", "WARN", "synthetic",
     "Stabilized is current behaviour; it should persist but not forever (synthetic ~60%).",
     "Too low: the band is too loose. Too high: frozen buckets (holidays) are read as payments."),
    ("E15", "Option A: straight-roller share",
     lambda R: float(_share(R, "A_minimal_4").get("straight_roller", 0)), lambda v: 0.55 <= v <= 0.80,
     "55–80%", "WARN", "bank",
     "Most accounts roll straight 2-3-4 (synthetic ~70%).",
     "If much lower, many run-ups contain a hold — look at E28 (artefacts) before trusting slow roller."),
    ("E16", "Smallest optional state in option B (EPD and stabilized are required; empty = 0)",
     lambda R: float(_share(R, "B_balanced_6").drop(["early_payment_default", "stabilized"]).min()),
     lambda v: v >= 0.05, ">= 5%", "WARN", "design",
     "Actionable size for the optional splits; the bank's two known states are kept at any size. "
     "Synthetic: early-life straight roller ~4.7% under the 12-month cut.",
     "If it is early-life straight roller: merge it into straight roller (agreed with the owner: set "
     "seasoned_min_months=None and keep early life as a flag). Any other state: escalate."),
    ("E17", "Option C: smaller of intermittent / erratic payer",
     lambda R: float(_share(R, "C_detailed_7").reindex(["slow_roller_intermittent", "slow_roller_erratic"]).fillna(0).min()),
     lambda v: v >= 0.04, ">= 4%", "WARN", "design",
     "Synthetic 10% / 6%.", "Too small to act on — use option B."),
    ("E18", "Stabilized sits low in the spine: share at bucket 4 / share at bucket 7",
     _by_bucket_ratio, lambda v: v >= 2, ">= 2x", "WARN", "bank",
     "90–95% roll rates at 6–7 leave little room to hold there.",
     "Stabilized accounts at 6–7 are unusual — check for frozen buckets (payment holidays)."),
    ("E19", "Orthogonality: credibility score explained by the states (eta²)",
     lambda R: _eta(R, "credibility_score"), lambda v: v <= 0.25, "<= 0.25", "WARN", "design",
     "Known overlap via stabilized (money in), slow roller (money in near bucket 4) and repeat "
     "delinquent (clean point); the states should not reproduce the score.",
     "Use option A (drops repeat delinquent) or report stabilized under credibility instead."),
    ("E19b", "Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²)",
     lambda R: _eta(R, "cred_clean_point"), lambda v: v <= 0.50, "<= 0.50", "WARN", "design",
     "Repeat delinquent uses earlier spells — the history the clean point scores (now limited to the "
     "last 24 months, which lowers the overlap).",
     "Repeat delinquent duplicates the clean point: use option A, or keep it and tell the persona grid "
     "it is the same signal (only 1 of credibility's 5 points)."),
    ("E20", "Orthogonality: ability score explained by the states (eta²)",
     lambda R: _eta(R, "ability_score"), lambda v: v <= 0.10, "<= 0.10", "WARN", "design",
     "DPD shape should carry little of salary/inflow/CASA.",
     "Straight vs slow roller may proxy income loss — fine, but say so in the persona grid."),
    ("E20b", "Orthogonality: reachability / in-country explained by the states (max eta²)",
     lambda R: _max_eta(R, ["reachable_flag", "in_country_flag"]), lambda v: v <= 0.05, "<= 0.05",
     "WARN", "design", "Locatability is independent of how the debt was paid.",
     "A state is acting as a departure proxy — report it to the persona owners."),
    ("E21", "Stabilized accounts with money coming in (credibility component or DPD proxy)",
     lambda R: R["overlap_other_axes"]["stabilized_vs_money_in"]["stabilized_with_money_in"],
     lambda v: v >= 0.90, ">= 90%", "WARN", "design",
     "Stabilized = paid one month's due most months, so money must be coming in.",
     "Stabilized accounts without money in are frozen buckets (holiday/restructure) — flag them."),
    ("E22", "INFO — residual clusters: option-B ARI gain over option A at k=6",
     _resid_gain, None, "report", "INFO", "synthetic",
     "Diagnostic only: any finer partition built on the clustered features gains ARI (a meaningless "
     "tenure split gained 0.16 in review), so this is not evidence for B over A.",
     "—"),
    ("E23", "INFO — one paid month: straight minus one-hold slow roller, next-month roll (bucket-std)",
     _one_hold, None, "report", "INFO", "synthetic",
     "41% of slow rollers rest on a single hold. Unknowable from synthetic data (same post-4 dynamics).",
     "Near 0 and E28 shows artefacts: the straight/slow split rests on noise — escalate whether a single "
     "hold should still make a slow roller (straight_max_runup = 4)."),
    ("E24", "'Paying since 4' stays rejected: share still in it next month at 0.5",
     _partial, lambda v: v <= 0.75, "<= 75%", "WARN", "synthetic",
     "Synthetic ~63%: an unstable current-behaviour state.",
     "If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'."),
    ("E25", "INFO — spread of exit to 8+ within 3 months across fixed states (option B, bucket-std)",
     _spread, None, "report", "INFO", "synthetic",
     "Standardised to the bucket mix and over 3 months, because 6-month exit saturates near 100% at 5–7.",
     ">= 5pp means how they fell in carries risk information beyond stabilized."),
    ("E26", "Stabilized bounce-backs: ever-stabilized accounts that left and came back within k months",
     _flips,
     lambda v: v <= 0.10, "<= 10%", "WARN", "synthetic",
     "Synthetic ~5–7% with the long-run clause vs ~8% on the bank's rule alone; oscillating payers "
     "bounce 41% less. Remaining bounces are mostly staircases (hold, step, hold).",
     "Too many bounce: look at shapes; +2 tolerance or a sticky rule widen the definition — escalate."),
    ("E27", "String lengths vary (p95 minus p05 of history length, months)",
     lambda R: R["data_quality"]["string_length_spread"], lambda v: v >= 6, ">= 6", "WARN", "data",
     "Full history from the first billed month gives very different lengths across accounts.",
     "Strings look fixed-length (padded or truncated): EPD and early-life cannot be judged from the "
     "string — confirm the convention (PROMPTS P1) before reading those states."),
    ("E28", "Run-up holds by calendar month: largest month vs its neighbours (artefact check)",
     lambda R: R.get("runup_hold_calendar_spike"), lambda v: v <= 2.5, "<= 2.5", "WARN", "data",
     "Customer payments spread over calendar months; a spike means a system event (cycle-date change, "
     "reversal batch, deferral).",
     "Find the month (section 5b) and ask the data owners; holds from that month should not count."),
]


def evaluate(R: dict) -> pd.DataFrame:
    rows = []
    for eid, title, metric, check, expected, sev, anchor, why, action in EXPECTATIONS:
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
                     "expected": expected, "anchor": anchor, "why": why, "if_not_met": action})
    return pd.DataFrame(rows)
