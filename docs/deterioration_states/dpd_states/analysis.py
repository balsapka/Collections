"""Real-data analysis of deterioration states — pure pandas, no Spark.

`run(current, latest_bt, cfg, spark_counts=None)` takes two small pandas frames that the
Spark snippet has already scoped and sampled:

    current    accounts in today's spine (current bucket 4–7): `dpd_string` plus any
               optional columns named as the keys of cfg.AXIS_COLS / EXISTING_RULE_COLS /
               FLAG_COLS.
    latest_bt  accounts that were in the spine k = cfg.BACKTEST_MONTHS months ago, with
               their string AS OF TODAY (k newer digits on the left). Dropping those k
               digits gives the string as it was k months ago; the dropped digits are what
               happened next. ASSUMES every string ends in the same (latest) month — strings
               frozen at charge-off or closure break this (see METHODOLOGY §8). None = no
               backtest (outcome checks are skipped).

Returns (results, markdown). Both hold aggregates only — no keys and no raw DPD strings;
examples are banded journey shapes shared by at least MIN_SHAPE_COUNT accounts.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd

from . import discover as dv
from .features import H, P, build_features, encode, _runs
from .states import (DISPLAY_NAMES, FIXED_STATES, OPTIONS, RECOMMENDED, REMARKS,
                     assign_states, option_states, order)

MIN_SHAPE_COUNT = 10          # governance: never show a journey shape rarer than this


# --- helpers ---------------------------------------------------------------------

def md(df: pd.DataFrame, index: bool = True, floatfmt: str = "{:.3f}") -> str:
    if df is None or len(df) == 0:
        return "_(empty)_"
    if index:
        df = df.reset_index()
    cells = [[floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in row]
             for row in df.itertuples(index=False)]
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "---|" * len(df.columns)
    return "\n".join([head, sep] + ["| " + " | ".join(r) + " |" for r in cells])


def _num(v):
    if isinstance(v, (float, np.floating)):
        return None if math.isnan(v) else round(float(v), 4)
    return v.item() if hasattr(v, "item") else v


def _records(df: pd.DataFrame) -> list[dict]:
    return [{str(k): _num(v) for k, v in r.items()} for r in df.reset_index().to_dict("records")]


def _json_safe(obj):
    """Recursively make results JSON-safe: str keys, NaN -> None, numpy -> python."""
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return _num(obj)


def clean_strings(s: pd.Series, char_map: dict, strip_chars: str, leftmost_is_current: bool = True):
    """Normalise strings; returns (clean series, valid mask). STRIP_CHARS are removed from
    the two ends only — removing them mid-string would shift every older month."""
    s = s.astype(str)
    if strip_chars:
        s = s.str.strip(strip_chars)
    for a, b in (char_map or {}).items():
        s = s.str.replace(a, b, regex=False)
    if not leftmost_is_current:
        s = s.str[::-1]
    valid = s.str.fullmatch(r"\d+").fillna(False).astype(bool) & (s.str.len() > 0)
    return s, valid


_TRUE = {"1", "y", "yes", "true", "t"}
_FALSE = {"0", "n", "no", "false", "f"}


def parse_flag(x: pd.Series) -> tuple[pd.Series, float]:
    """1/0, Y/N, Yes/No, True/False (any case) -> bool. Returns (flag, share unparsed)."""
    t = x.astype(str).str.strip().str.lower()
    known = t.isin(_TRUE | _FALSE)
    return t.isin(_TRUE), float(1 - known[x.notna()].mean()) if x.notna().any() else 1.0


def crop_history(s: pd.Series, max_len: int | None) -> tuple[pd.Series, pd.Series]:
    """Keep the newest max_len months (leftmost digits) — history older than the window is
    dropped. A string that fills the whole window may have older history, so it is flagged
    as cropped too (>=). Returns (cropped strings, cropped flag)."""
    if not max_len:
        return s, pd.Series(False, index=s.index)
    return s.str[:max_len], s.str.len() >= max_len


def _spells(s: str, from_bucket: int, how: str) -> int:
    """'reached': runs at >=2 that reached the bucket; 'at': runs of months at >= the bucket."""
    b = encode(s)[0]
    if how == "reached":
        return sum(1 for a, e in _runs(b >= 2) if b[a:e].max() >= from_bucket)
    return len(_runs(b >= from_bucket))


def _eta2(y: pd.Series, g: pd.Series) -> float:
    """Share of the variance of an axis score explained by the state (0 = orthogonal)."""
    y = pd.to_numeric(y, errors="coerce")
    ok = y.notna()
    y, g = y[ok], g[ok]
    if len(y) < 2 or y.var() == 0:
        return float("nan")
    means = y.groupby(g).transform("mean")
    return float(((means - y.mean()) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def _ari(a, b) -> float:
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(a, b))


def _std_rate(outcome: pd.Series, state: pd.Series, bucket: pd.Series) -> pd.Series:
    """Outcome rate per state, standardised to the population's current-bucket mix, so a
    state concentrated at bucket 4 is not flattered (or penalised) by where it sits."""
    mix = bucket.value_counts(normalize=True)
    rates = outcome.astype(float).groupby([state, bucket]).mean().unstack()
    out = {}
    for s_, row in rates.iterrows():
        w = mix[row.dropna().index]
        out[s_] = float((row.dropna() * w).sum() / w.sum()) if w.sum() else float("nan")
    return pd.Series(out)


# --- backtest frame ---------------------------------------------------------------

def backtest_frame(latest: pd.Series, k: int, spine, exit_bucket: int) -> pd.DataFrame:
    """From today's strings, rebuild the spine as of k months ago plus what happened next."""
    latest = latest[latest.str.len() > k]
    as_of = latest.str[k:]
    in_spine = as_of.str[0].astype(int).isin(spine)
    latest, as_of = latest[in_spine], as_of[in_spine]
    fut = latest.str[:k]                                   # newest first
    digits = fut.apply(lambda x: [int(ch) for ch in x])
    return pd.DataFrame({
        "dpd_string": as_of,
        "next_bucket": latest.str[k - 1].astype(int),
        "next_string": latest.str[k - 1:],
        "bucket_k": latest.str[0].astype(int),
        "exit_k": digits.apply(lambda d: max(d) >= exit_bucket),
        "exit_3m": digits.apply(lambda d: max(d[-3:]) >= exit_bucket),   # first 3 future months
        "cure_k": digits.apply(lambda d: min(d) <= 1),
    })


def backtest_scorecard(f: pd.DataFrame, state: pd.Series, state_next: pd.Series, spine) -> pd.DataFrame:
    g = f.assign(state=state)
    rolled = g.next_bucket >= g.b_now + 1
    out = pd.DataFrame({"share": g.state.value_counts(normalize=True),
                        "n": g.state.value_counts()})
    out["roll_next_month"] = rolled.groupby(g.state).mean()
    out["roll_next_month_bucket_std"] = _std_rate(rolled, g.state, g.b_now)
    out["exit_8plus_within_3m_bucket_std"] = _std_rate(g.exit_3m, g.state, g.b_now)
    out["exit_8plus_within_k"] = g.groupby("state").exit_k.mean()
    out["cure_within_k"] = g.groupby("state").cure_k.mean()
    out["median_bucket_change_k"] = (g.bucket_k.clip(upper=9) - g.b_now).groupby(g.state).median()
    idx = state_next.index
    out["same_state_next_month"] = (state.loc[idx] == state_next).groupby(state.loc[idx]).mean()
    kept = (state.loc[idx] == state_next) | (state_next == "stabilized")
    out["kept_or_stabilized_next_month"] = kept.groupby(state.loc[idx]).mean()
    out["left_spine_next_month"] = (~g.next_bucket.isin(spine)).groupby(g.state).mean()
    return out.loc[order(out.index)]


def stabilized_flips(latest: pd.Series, k: int, spine, n: int = 10_000, seed: int = 7,
                     truncated: pd.Series | None = None) -> dict:
    """Month-by-month stabilized status over the k backtest months, for a sample of the
    backtest population. A 'bounce-back' is an account that LEFT stabilized and later came
    BACK while staying in the spine (S . S). Entering once and leaving once (. S S .) is a
    normal lifecycle and is not counted. Reported with and without the long-run clause."""
    latest = latest[latest.str.len() > k]
    latest = latest.sample(min(n, len(latest)), random_state=seed)
    tr = truncated if truncated is not None else pd.Series(False, index=latest.index)
    rows = [{"acct": i, "j": j, "dpd_string": s_[k - j:], "history_truncated": bool(tr.get(i, False))}
            for i, s_ in latest.items() for j in range(k + 1)]
    panel = pd.DataFrame(rows)
    panel = panel[panel.dpd_string.str[0].astype(int).isin(spine)]
    out = {"n_accounts": int(latest.size)}
    if not len(panel):
        return out
    pf = build_features(panel)
    for name, kw in (("with_long_run_clause", {}), ("bank_rule_only", {"stabilized_long_run_months": None})):
        st = (assign_states(pf, **OPTIONS[RECOMMENDED], **kw) == "stabilized")
        g = pf.assign(stab=st).sort_values(["acct", "j"])
        cons = g.groupby("acct").j.diff() == 1
        prev = g.groupby("acct").stab.shift(1, fill_value=False).astype(bool)
        left = cons & prev & ~g.stab
        left_before = left.groupby(g.acct).cumsum() - left
        back = cons & ~prev & g.stab & (left_before > 0)
        bounced = back.groupby(g.acct).any()
        changes = (cons & (prev != g.stab)).groupby(g.acct).sum()
        ever = g.groupby("acct").stab.any()
        out[name] = {"ever_stabilized": float(ever.mean()),
                     "bounce_back_share_of_ever_stabilized": float(bounced[ever].mean()) if ever.any() else None,
                     "mean_status_changes_per_account": float(changes.mean())}
    return out


def runup_hold_calendar(f: pd.DataFrame, max_months_ago: int = 36) -> pd.DataFrame:
    """When did run-up holds happen, in calendar months before today? Strings share an
    as-of month, so a spike at one 'months ago' means a system artefact (cycle-date change,
    reversal batch, deferral), not customer behaviour."""
    counts = pd.Series(0, index=range(1, max_months_ago + 1), dtype=float)
    for s in f.dpd_string[f.runup_holds > 0]:
        b, d, c = encode(s)
        ep = _runs(b >= 2)[-1]
        first4 = ep[0] + int(np.argmax(b[ep[0]:ep[1]] >= 4))
        for t in range(max(ep[0] - 1, 0), first4):
            if c[t] == H:
                ago = len(b) - 1 - (t + 1)
                if 1 <= ago <= max_months_ago:
                    counts[ago] += 1
    total = counts.sum()
    return (counts / total).rename("share_of_runup_holds").rename_axis("months_ago").to_frame() if total else counts.to_frame()


# --- main ----------------------------------------------------------------------------

def run(current: pd.DataFrame, latest_bt: pd.DataFrame | None, cfg, spark_counts: dict | None = None,
        seed: int = 7):
    k = cfg.BACKTEST_MONTHS
    spine = tuple(cfg.SPINE_BUCKETS)
    R, M = {}, []            # results (JSON) and markdown sections

    # ---- data quality + current spine --------------------------------------------
    max_len = getattr(cfg, "MAX_HISTORY_MONTHS", None)
    s, ok = clean_strings(current.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
    s, trunc = crop_history(s, max_len)
    cur = current.assign(dpd_string=s, history_truncated=trunc)[ok]
    cur = cur[cur.dpd_string.str[0].astype(int).isin(spine)]
    if not len(cur):
        raise ValueError("no account in today's spine after cleaning — check COL_DPD, "
                         "LEFTMOST_IS_CURRENT, CHAR_MAP and SPINE_BUCKETS in config.py")
    f = build_features(cur)
    opts = {o: assign_states(f, **kw) for o, kw in OPTIONS.items()}
    f["state"] = opts[RECOMMENDED]

    q = f.hist_len.quantile([.05, .5, .95])
    dq = {
        "n_current_rows": int(len(current)),
        "share_invalid_strings_current": float(1 - ok.mean()),
        "share_non_digit_strings_table": (float(spark_counts["non_digit_strings"] / max(spark_counts["rows"], 1))
                                          if spark_counts else None),
        "n_current_spine_analysed": int(len(f)),
        "max_history_months": max_len,
        "share_history_cropped_to_window": float(f.history_truncated.mean()),
        "share_spell_started_before_window": float((f.left_censored & f.history_truncated).mean()),
        "string_length_p05_p50_p95": [int(x) for x in q],
        "string_length_spread": (int(f.hist_len[~f.history_truncated].quantile(.95)
                                     - f.hist_len[~f.history_truncated].quantile(.05))
                                 if (~f.history_truncated).sum() >= 20 else None),
        "share_history_starts_delinquent": float((f.left_censored & ~f.history_truncated).mean()),
        "share_glitch_fixed": float((f.n_glitches > 0).mean()),
        "share_jump_repaired": float((f.n_jumps_repaired > 0).mean()),
        "share_jump_left": float((f.n_jumps_left > 0).mean()),
        "one_spell_share": {f"{how}_{x}": float((f.dpd_string.map(lambda v: _spells(v, x, how)) == 1).mean())
                            for how in ("reached", "at") for x in (3, 4)},
        "bucket_mix": {str(b): float(v) for b, v in f.b_now.value_counts(normalize=True).sort_index().items()},
    }
    R["data_quality"] = dq
    R["state_names"] = {s_: {"display": DISPLAY_NAMES[s_], "remark": REMARKS[s_]} for s_ in DISPLAY_NAMES}
    M.append("## State names\n\n" + md(pd.DataFrame(
        [{"code": s_, "display name": DISPLAY_NAMES[s_], "remark": REMARKS[s_]} for s_ in DISPLAY_NAMES]),
        index=False))
    dq_tbl = {kk: v for kk, v in dq.items() if not isinstance(v, dict)}
    M.append("## 1. Data quality and population\n\n" + md(pd.Series(dq_tbl, name="value").rename_axis("metric").to_frame())
             + "\n\nShare of the spine with ONE spell only, by definition (the bank quotes ~85% — "
             "the matching row tells which definition the bank uses):\n\n"
             + md(pd.Series({"run at >=2 that reached 3": dq["one_spell_share"]["reached_3"],
                             "run at >=2 that reached 4": dq["one_spell_share"]["reached_4"],
                             "run of months at >=3": dq["one_spell_share"]["at_3"],
                             "run of months at >=4": dq["one_spell_share"]["at_4"]},
                            name="share").rename_axis("spell definition").to_frame()))

    # ---- states today, all options ----------------------------------------------
    R["states_today"] = {}
    parts = ["## 2. States today (current spine)"]
    for o, st in opts.items():
        allowed = option_states(o)
        share = st.value_counts(normalize=True).reindex(allowed, fill_value=0.0).rename_axis("state")
        by_b = pd.crosstab(st, f.b_now, normalize="columns").reindex(allowed, fill_value=0.0)
        by_b = by_b.rename_axis(index="state", columns="bucket")
        R["states_today"][o] = {"share": share.round(4).to_dict(),
                                "by_bucket": {str(c): by_b[c].round(4).to_dict() for c in by_b.columns},
                                "mece": bool(st.notna().all()),
                                "n_unknown_state": int((~st.isin(allowed)).sum())}
        parts.append(f"### {o}\n\nShare:\n\n" + md(share.to_frame("share"))
                     + "\n\nMix by current bucket (column shares):\n\n" + md(by_b))
    shp = f.assign(shape=f.dpd_string.map(dv.shape)).groupby(["state", "shape"]).size().rename("accounts")
    shp = shp[shp >= MIN_SHAPE_COUNT].reset_index()
    shp = shp.sort_values(["state", "accounts"], ascending=[True, False]).groupby("state").head(3)
    shp = shp.sort_values("state", key=lambda x: x.map({s_: i for i, s_ in enumerate(order(x))}))
    parts.append(f"Most common journey shapes per state ({RECOMMENDED}; N clean, R roll, H hold, P paid "
                 f"2+ months; only shapes shared by >= {MIN_SHAPE_COUNT} accounts):\n\n" + md(shp, index=False))
    M.append("\n\n".join(parts))

    # ---- agreement with the bank's existing rules -------------------------------
    agree = {}
    for col, ours in (("existing_bust_out", "early_payment_default"), ("existing_stabilized", "stabilized")):
        if col in f and f[col].notna().any():
            theirs, unparsed = parse_flag(f[col])
            if unparsed > 0.5:
                agree[ours] = {"skipped": f"{unparsed:.0%} of {col} values not recognised as 1/0, Y/N, True/False"}
                continue
            mine = f.state == ours
            agree[ours] = {"their_share": float(theirs.mean()), "our_share": float(mine.mean()),
                           "recall_of_theirs": float((mine & theirs).sum() / max(theirs.sum(), 1)),
                           "precision_vs_theirs": float((mine & theirs).sum() / max(mine.sum(), 1)),
                           "share_unparsed": unparsed}
    R["existing_rule_agreement"] = agree or "SKIPPED (no existing rule columns configured)"
    M.append("## 3. Agreement with the bank's existing EPD ('bust-out') / stabilized rules\n\n"
             + (md(pd.DataFrame(agree).T.rename_axis("state")) if agree else "_Skipped — no existing rule columns configured._"))

    # ---- overlap with the other persona axes ------------------------------------
    axes = [c for c in cfg.AXIS_COLS if c in f and f[c].notna().any()]
    ov = {}
    if axes:
        eta = pd.DataFrame({o: {a: _eta2(f[a], st) for a in axes} for o, st in opts.items()}).rename_axis("axis")
        means = f.groupby("state")[axes].agg(lambda x: pd.to_numeric(x, errors="coerce").mean())
        means = means.loc[order(means.index)]
        ov = {"eta2_by_option": _records(eta), "mean_by_state": _records(means)}
        txt = ("Variance of each axis explained by the states (eta², 0 = orthogonal):\n\n" + md(eta)
               + f"\n\nMean of each axis by state ({RECOMMENDED}):\n\n" + md(means))
    else:
        txt = "_No axis columns configured — using the DPD proxy for 'money coming in' only._"
    money = "cred_money_in_points" if "cred_money_in_points" in axes else None
    paid_now = (pd.to_numeric(f[money], errors="coerce") > 0) if money else f.paid_any_3m
    stab = f.state == "stabilized"
    ov["stabilized_vs_money_in"] = {"source": money or "DPD proxy (paid >= 1 month in last 3)",
                                    "stabilized_with_money_in": float(paid_now[stab].mean()) if stab.any() else None,
                                    "others_with_money_in": float(paid_now[~stab].mean())}
    mib = paid_now.groupby([f.state, f.b_now]).mean().unstack()
    mib = mib.loc[order(mib.index)].rename_axis(index="state", columns="bucket")
    ov["money_in_by_state_and_bucket"] = {str(c): mib[c].round(4).to_dict() for c in mib.columns}
    flags = {}
    for c in cfg.FLAG_COLS:
        if c in f and f[c].notna().any():
            fl, unparsed = parse_flag(f[c])
            flags[c] = float(fl[stab].mean()) if unparsed <= 0.5 else None
    ov["stabilized_flagged"] = flags
    R["overlap_other_axes"] = ov
    M.append("## 4. Overlap with the other persona axes\n\n" + txt + "\n\nStabilized vs money coming in:\n\n"
             + md(pd.Series(ov["stabilized_vs_money_in"], name="value").rename_axis("metric").to_frame())
             + "\n\nMoney coming in by state and current bucket (slow rollers paid on the way down, so "
             "near bucket 4 they overlap credibility's 'money in' — a clock effect):\n\n" + md(mib)
             + ("\n\nShare of stabilized accounts carrying a data flag (frozen bucket, not a payment):\n\n"
                + md(pd.Series(flags, name="share").to_frame()) if flags else ""))

    # ---- backtest: outcomes and stability ----------------------------------------
    bt = nf = None
    if latest_bt is not None and len(latest_bt):
        s2, ok2 = clean_strings(latest_bt.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
        dq["share_invalid_strings_backtest"] = float(1 - ok2.mean())
        s2, trunc2 = crop_history(s2[ok2], max_len)
        btf = backtest_frame(s2, k, spine, cfg.EXIT_BUCKET)
        btf["history_truncated"] = trunc2.loc[btf.index]
        ok2 = pd.Series(True, index=s2.index)
    else:
        btf = None
    if btf is not None and len(btf):
        bt = build_features(btf)
        nxt = (btf[btf.next_bucket.isin(spine)][["next_string", "history_truncated"]]
               .rename(columns={"next_string": "dpd_string"}))
        nf = build_features(nxt) if len(nxt) else None
        roll = (bt.next_bucket >= bt.b_now + 1).groupby(bt.b_now).mean()
        R["backtest"] = {"k_months": k, "n_analysed": int(len(bt)),
                         "share_exited_within_k": float(bt.exit_k.mean()),
                         "monthly_roll_rate": {str(b): float(v) for b, v in roll.items()},
                         "scorecards": {}}
        parts = [f"## 5. Backtest — spine as of {k} months ago, outcomes since\n\n"
                 f"{len(bt):,} accounts. Monthly roll rate by bucket (should match the bank's "
                 "~70/80/90/95%):\n\n" + md(roll.rename_axis("bucket").to_frame("roll_rate"))]
        for o, kw in OPTIONS.items():
            nxt_st = assign_states(nf, **kw) if nf is not None else pd.Series(dtype=object)
            card = backtest_scorecard(bt, assign_states(bt, **kw), nxt_st, spine)
            R["backtest"]["scorecards"][o] = _records(card)
            parts.append(f"### {o}\n\n" + md(card))
        # slow roller resting on a single paid month vs straight roller
        a_bt = assign_states(bt, **OPTIONS["A_minimal_4"])
        one = (a_bt == "slow_roller") & (bt.runup_holds == 1) & (bt.runup_pays == 0)
        grp = pd.Series(np.select([one, a_bt == "slow_roller", a_bt == "straight_roller"],
                                  ["slow roller: exactly one hold", "slow roller: more than one payment",
                                   "straight roller"], "other"), index=bt.index)
        keep = grp != "other"
        rolled = bt.next_bucket >= bt.b_now + 1
        one_hold = pd.DataFrame({
            "share_of_spine": grp[keep].value_counts() / len(bt),
            "roll_next_month_bucket_std": _std_rate(rolled[keep], grp[keep], bt.b_now[keep]),
            "exit_8plus_within_3m_bucket_std": _std_rate(bt.exit_3m[keep], grp[keep], bt.b_now[keep])})
        R["backtest"]["one_hold_slow_rollers"] = _records(one_hold)
        parts.append("### Is one paid month enough to separate slow from straight rollers?\n\n"
                     + md(one_hold.rename_axis("group")))
        flips = stabilized_flips(s2, k, spine, seed=seed, truncated=trunc2)
        R["backtest"]["stabilized_flips"] = flips
        parts.append(f"### Stabilized bounce-backs over the {k} backtest months "
                     f"({flips['n_accounts']:,} accounts)\n\nShare of ever-stabilized accounts that left "
                     "stabilized and came back while staying in the spine (S . S):\n\n"
                     + md(pd.DataFrame({kk: v for kk, v in flips.items() if isinstance(v, dict)}).T
                          .rename_axis("stabilized rule")))
        M.append("\n\n".join(parts))
    else:
        R["backtest"] = ("SKIPPED (no backtest population: outcomes need strings for accounts that have "
                         "since left the spine — a snapshot of today's segment is survivor-only)")
        # What a snapshot CAN show: stability among accounts that stayed in the spine.
        prev = f[f.dpd_string.str.len() > 1].dpd_string.str[1:]
        prev = prev[prev.str[0].astype(int).isin(spine)]
        prev_tr = f.loc[prev.index, "history_truncated"]
        surv = {"note": "survivor-only: accounts in the spine both last month and today"}
        if len(prev):
            pf = build_features(prev.to_frame("dpd_string").assign(history_truncated=prev_tr))
            st_prev = assign_states(pf, **OPTIONS[RECOMMENDED])
            now = f.loc[pf.index, "state"]
            same = pd.DataFrame({
                "same_state_next_month": (st_prev == now).groupby(st_prev).mean(),
                "kept_or_stabilized_next_month": ((st_prev == now) | (now == "stabilized")).groupby(st_prev).mean(),
                "n": st_prev.value_counts()})
            same = same.loc[order(same.index)]
            surv["same_state_next_month"] = _records(same.rename_axis("state"))
        surv["stabilized_flips"] = stabilized_flips(f.dpd_string, k, spine, seed=seed,
                                                    truncated=f.history_truncated)
        R["survivor_checks"] = surv
        M.append("## 5. Backtest\n\n_Skipped — outcomes (roll rates, exits) need strings for accounts that "
                 "have since left the spine; a snapshot of today's segment only has the survivors._\n\n"
                 "### Survivor-only stability (accounts in the spine last month and today)\n\n"
                 + (md(same) if len(prev) else "_(none)_")
                 + f"\n\nStabilized bounce-backs over the last {k} months:\n\n"
                 + md(pd.DataFrame({kk: v for kk, v in surv["stabilized_flips"].items() if isinstance(v, dict)}).T
                      .rename_axis("stabilized rule")))

    # ---- run-up holds by calendar month (artefact check) ---------------------------
    cal = runup_hold_calendar(f)
    if len(cal) and cal.iloc[:, 0].sum():
        v = cal.iloc[:, 0]
        # a month compared with the median of its neighbours (±2 months): the natural shape
        # (more holds in recent months) cancels out, a one-month system event does not
        ratios = {}
        for m in v.index:
            nb_ = v[[x for x in range(m - 2, m + 3) if x != m and x in v.index]]
            base_ = float(nb_.median())
            if base_ > 0 and v[m] * len(f) >= 20:                 # ignore near-empty months
                ratios[m] = float(v[m] / base_)
        R["runup_hold_calendar_spike"] = max(ratios.values()) if ratios else None
        R["runup_hold_calendar"] = {str(i): float(x) for i, x in v.items()}
        spike = R["runup_hold_calendar_spike"]
        M.append("## 5b. Run-up holds by calendar month (months before today)\n\nEach month is "
                 "compared with its neighbours (±2 months); a month far above them points to a system "
                 "artefact (cycle-date change, reversal batch, deferral), not customer behaviour. "
                 f"Largest month / neighbour-median ratio: {spike if spike is None else round(spike, 2)}\n\n" + md(cal))

    # ---- threshold sweeps (on the backtest population when available) ------------
    base = bt if bt is not None else f
    nb = nf if bt is not None else None
    sw = {}

    def _stay(kw, name):
        if nb is None:
            return None
        a, b = assign_states(base, **kw), assign_states(nb, **kw)
        m = (a == name).loc[nb.index]
        return float((b[m[m].index] == name).mean()) if m.any() else None

    rows = []
    for v in (2, 3, 4, 6, 9, 12):
        st = assign_states(base, epd_max_history=v)
        b_ = st == "early_payment_default"
        rows.append({"epd_max_history": v, "share": b_.mean(),
                     "exit_within_k": base.exit_k[b_].mean() if bt is not None and b_.any() else None})
    sw["epd_max_history"] = rows
    rows = []
    for v in (4, 5, 6):
        st = assign_states(base, stabilized_min_in_band=v)
        h = st == "stabilized"
        rows.append({"stabilized_min_in_band": v, "share": h.mean(),
                     "roll_next_month": (base.next_bucket[h] >= base.b_now[h] + 1).mean() if bt is not None and h.any() else None,
                     "still_stabilized_next_month": _stay({"stabilized_min_in_band": v}, "stabilized")})
    sw["stabilized_min_in_band"] = rows
    rows = []
    for v in (2, 3, 4):
        for w in (12, 24, 36, 9999):
            st = assign_states(base, **{**OPTIONS[RECOMMENDED], "repeat_min_prior_peak": v, "repeat_window_months": w})
            rows.append({"repeat_min_prior_peak": v, "repeat_window_months": "any" if w == 9999 else w,
                         "share": (st == "repeat_delinquent").mean()})
    sw["repeat_delinquent"] = rows
    rows = []
    for v in (3, 4, 5):
        st = assign_states(base, straight_max_runup=v)
        rows.append({"straight_max_runup": v, "straight_share": (st == "straight_roller").mean(),
                     "slow_share": (st == "slow_roller").mean()})
    sw["straight_max_runup"] = rows
    rows = []
    for v in (12, 18, 24, 36):
        st = assign_states(base, **{**OPTIONS[RECOMMENDED], "seasoned_min_months": v})
        rows.append({"seasoned_min_months": v, "seasoned": (st == "straight_roller_seasoned").mean(),
                     "early_life": (st == "straight_roller_early_life").mean()})
    sw["seasoned_min_months"] = rows
    rows = []
    for v in (0.34, 0.5, 0.67):
        kw = {**OPTIONS["C_detailed_7"], "paying_since_4_min_rate": v}
        st = assign_states(base, **kw)
        row = {"paying_since_4_min_rate": v, "share": (st == "paying_since_4").mean(),
               "still_paying_since_4_next_month": _stay(kw, "paying_since_4")}
        if nb is not None:
            st2 = assign_states(nb, **kw)
            fixed = st.loc[nb.index].isin(FIXED_STATES)
            row["stability_of_fixed_states"] = float((st.loc[nb.index][fixed] == st2[fixed]).mean())
            kw0 = OPTIONS["C_detailed_7"]
            a0, b0 = assign_states(base, **kw0).loc[nb.index], assign_states(nb, **kw0)
            fx0 = a0.isin(FIXED_STATES)
            row["stability_of_fixed_states_without_q3"] = float((a0[fx0] == b0[fx0]).mean())
        rows.append(row)
    sw["paying_since_4_test"] = rows
    R["sweeps"] = {kk: [{a: _num(b) for a, b in r.items()} for r in v] for kk, v in sw.items()}
    M.append("## 6. Threshold sweeps (" + ("backtest population" if bt is not None else "current spine")
             + "). Parameters marked [business] in states.py are agreed definitions — the sweeps "
             "show sensitivity; they are not a menu for matching a share.\n\n"
             + "\n\n".join(f"### {kk}\n\n" + md(pd.DataFrame(v), index=False) for kk, v in sw.items()))

    # ---- residual clustering agreement (diagnostic only) ---------------------------
    a_states = opts["A_minimal_4"]
    r = f[~a_states.isin(["early_payment_default", "stabilized", "history_starts_delinquent"])]
    if len(r) > 30_000:
        r = r.sample(30_000, random_state=seed)
    if len(r) >= 50:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        feats = ["months_before_spell", "n_blips", "n_prior_episodes", "max_prior_bucket",
                 "clean_gap_before_current", "runup_len", "runup_holds", "runup_pays",
                 "post4_paid_rate", "rec_paid_rate"]
        X = r[feats].astype(float).copy()
        for c in ("months_before_spell", "clean_gap_before_current", "runup_len"):
            X[c] = np.log1p(X[c])
        X = StandardScaler().fit_transform(X)
        rows = []
        for kk in range(2, 9):
            lab = KMeans(kk, n_init=10, random_state=seed).fit_predict(X)
            rows.append({"k": kk, **{f"agree_{o}": _ari(lab, st.loc[r.index]) for o, st in opts.items()}})
        R["residual_cluster_agreement"] = rows
        M.append("## 7. Clustering the residual (after EPD and stabilized) — agreement (ARI) with each "
                 "option. Diagnostic only: a finer partition built on the clustered features always "
                 "gains ARI, so this is not evidence for B over A.\n\n" + md(pd.DataFrame(rows), index=False))
    else:
        R["residual_cluster_agreement"] = "SKIPPED (fewer than 50 residual accounts)"

    # ---- shapes and motifs ---------------------------------------------------------
    smp = f.sample(min(len(f), 30_000), random_state=seed)
    shapes = dv.shape_table(smp, label="state", top=20)
    shapes = shapes[shapes.n >= MIN_SHAPE_COUNT]
    grams = dv.ngram_table(smp, n=4, label="state", top=15)
    R["top_shapes"] = _records(shapes.set_index("shape"))
    R["top_4grams"] = _records(grams.set_index("gram")) if len(grams) else []
    M.append("## 8. Most common journey shapes and motifs\n\nShapes (N clean, R roll, H hold = paid "
             f"one month, P paid 2+ months; run lengths banded; shared by >= {MIN_SHAPE_COUNT} accounts):\n\n"
             + md(shapes, index=False) + "\n\n4-grams by lift vs shuffled order:\n\n" + md(grams, index=False))

    return _json_safe(R), "\n\n".join(M)
