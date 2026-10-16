"""Real-data analysis of deterioration states — pure pandas, no Spark.

`run(current, latest_bt, cfg)` takes two small pandas frames that the Spark snippet has
already scoped and sampled:

    current    accounts in today's spine (current bucket 4–7): `dpd_string` plus any
               optional columns named as the keys of cfg.AXIS_COLS / EXISTING_RULE_COLS /
               FLAG_COLS.
    latest_bt  accounts that were in the spine k = cfg.BACKTEST_MONTHS months ago, with
               their string AS OF TODAY (k newer digits on the left). Dropping those k
               digits gives the string as it was k months ago; the dropped digits are what
               happened next. None = no backtest (outcome checks are skipped).

Returns (results, markdown). `results` is JSON-serialisable aggregates only — no keys,
no row-level data — so it can be committed. The markdown adds a handful of example
DPD strings (no keys) for eyeballing.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from . import discover as dv
from .features import build_features, encode, _runs
from .states import (DISPLAY_NAMES, FIXED_STATES, OPTIONS, RECOMMENDED, REMARKS,
                     assign_states, order)


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


def _records(df: pd.DataFrame) -> list[dict]:
    out = df.reset_index().replace({np.nan: None})
    return [{k: (round(v, 4) if isinstance(v, (float, np.floating)) else
                 (v.item() if hasattr(v, "item") else v)) for k, v in r.items()}
            for r in out.to_dict("records")]


def clean_strings(s: pd.Series, char_map: dict, strip_chars: str, leftmost_is_current: bool = True):
    """Normalise strings; returns (clean series, valid mask)."""
    s = s.astype(str)
    if strip_chars:
        s = s.str.replace(f"[{re.escape(strip_chars)}]", "", regex=True)
    for a, b in (char_map or {}).items():
        s = s.str.replace(a, b, regex=False)
    if not leftmost_is_current:
        s = s.str[::-1]
    valid = s.str.fullmatch(r"\d+").fillna(False) & (s.str.len() > 0)
    return s, valid


def _spells(s: str, from_bucket: int) -> int:
    b = encode(s)[0]
    return sum(1 for a, e in _runs(b >= 2) if b[a:e].max() >= from_bucket)


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
        "cure_k": digits.apply(lambda d: min(d) <= 1),
    })


def backtest_scorecard(f: pd.DataFrame, state: pd.Series, state_next: pd.Series) -> pd.DataFrame:
    g = f.assign(state=state)
    out = pd.DataFrame({"share": g.state.value_counts(normalize=True),
                        "n": g.state.value_counts()})
    out["roll_next_month"] = (g.next_bucket >= g.b_now + 1).groupby(g.state).mean()
    out["exit_8plus_within_k"] = g.groupby("state").exit_k.mean()
    out["cure_within_k"] = g.groupby("state").cure_k.mean()
    out["median_bucket_change_k"] = (g.bucket_k.clip(upper=9) - g.b_now).groupby(g.state).median()
    idx = state_next.index
    out["same_state_next_month"] = (state.loc[idx] == state_next).groupby(state.loc[idx]).mean()
    out["left_spine_next_month"] = (~g.next_bucket.between(4, 7)).groupby(g.state).mean()
    return out.loc[order(out.index)]


# --- main ----------------------------------------------------------------------------

def run(current: pd.DataFrame, latest_bt: pd.DataFrame | None, cfg, seed: int = 7):
    k = cfg.BACKTEST_MONTHS
    spine = tuple(cfg.SPINE_BUCKETS)
    R, M = {}, []            # results (JSON) and markdown sections
    rng = np.random.default_rng(seed)

    # ---- data quality + current spine --------------------------------------------
    s, ok = clean_strings(current.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
    cur = current.assign(dpd_string=s)[ok]
    cur = cur[cur.dpd_string.str[0].astype(int).isin(spine)]
    f = build_features(cur)
    f["state"] = assign_states(f, **OPTIONS[RECOMMENDED])
    opts = {o: assign_states(f, **kw) for o, kw in OPTIONS.items()}

    one3 = (f.dpd_string.map(lambda x: _spells(x, 3)) == 1).mean()
    one4 = (f.dpd_string.map(lambda x: _spells(x, 4)) == 1).mean()
    dq = {
        "n_current_rows": int(len(current)),
        "share_invalid_strings": float(1 - ok.mean()),
        "n_current_spine_analysed": int(len(f)),
        "string_length_p05_p50_p95": [int(x) for x in f.hist_len.quantile([.05, .5, .95])],
        "share_left_censored": float(f.left_censored.mean()),
        "share_jump_repaired": float((f.n_jumps_repaired > 0).mean()),
        "share_jump_left": float((f.n_jumps_left > 0).mean()),
        "share_one_spell_from3": float(one3),
        "share_one_spell_from4": float(one4),
        "bucket_mix": {int(b): float(v) for b, v in f.b_now.value_counts(normalize=True).sort_index().items()},
    }
    R["data_quality"] = dq
    R["state_names"] = {s: {"display": DISPLAY_NAMES[s], "remark": REMARKS[s]} for s in DISPLAY_NAMES}
    M.append("## State names\n\n" + md(pd.DataFrame(
        [{"code": s, "display name": DISPLAY_NAMES[s], "remark": REMARKS[s]} for s in DISPLAY_NAMES]),
        index=False))
    M.append("## 1. Data quality and population\n\n" + md(pd.Series(dq, name="value").rename_axis("metric").to_frame()))

    # ---- states today, all options ----------------------------------------------
    R["states_today"] = {}
    parts = ["## 2. States today (current spine)"]
    for o, st in opts.items():
        share = st.value_counts(normalize=True)
        by_b = pd.crosstab(st, f.b_now, normalize="columns")
        share = share.loc[order(share.index)].rename_axis("state")
        by_b = by_b.loc[order(by_b.index)].rename_axis(index="state", columns="bucket")
        R["states_today"][o] = {"share": share.round(4).to_dict(),
                                "by_bucket": {int(c): by_b[c].round(4).to_dict() for c in by_b.columns},
                                "mece": bool(st.notna().all())}
        parts.append(f"### {o}\n\nShare:\n\n" + md(share.to_frame("share"))
                     + "\n\nMix by current bucket (column shares):\n\n" + md(by_b))
    ex = (f.sample(frac=1.0, random_state=seed).groupby("state").head(3)[["state", "dpd_string"]]
          .sort_values("state", key=lambda x: x.map({s: i for i, s in enumerate(order(x))}))
          .assign(last_30_months_oldest_to_newest=lambda x: x.dpd_string.str[:30].str[::-1]))
    parts.append(f"Examples ({RECOMMENDED}, no keys):\n\n"
                 + md(ex[["state", "last_30_months_oldest_to_newest"]], index=False))
    M.append("\n\n".join(parts))

    # ---- agreement with the bank's existing rules -------------------------------
    agree = {}
    for col, ours in (("existing_bust_out", "early_payment_default"), ("existing_stabilized", "stabilized")):
        if col in f and f[col].notna().any():
            theirs = pd.to_numeric(f[col], errors="coerce").fillna(0).astype(bool)
            mine = f.state == ours
            agree[ours] = {"their_share": float(theirs.mean()), "our_share": float(mine.mean()),
                           "recall_of_theirs": float((mine & theirs).sum() / max(theirs.sum(), 1)),
                           "precision_vs_theirs": float((mine & theirs).sum() / max(mine.sum(), 1))}
    R["existing_rule_agreement"] = agree or "SKIPPED (no existing rule columns configured)"
    M.append("## 3. Agreement with the bank's existing EPD ('bust-out') / stabilized rules\n\n"
             + (md(pd.DataFrame(agree).T.rename_axis("state")) if agree else "_Skipped — no existing rule columns configured._"))

    # ---- overlap with the other persona axes ------------------------------------
    axes = [c for c in cfg.AXIS_COLS if c in f and f[c].notna().any()]
    ov = {}
    if axes:
        eta = pd.DataFrame({o: {a: _eta2(f[a], st) for a in axes} for o, st in opts.items()})
        means = f.groupby("state")[axes].agg(lambda x: pd.to_numeric(x, errors="coerce").mean())
        means = means.loc[order(means.index)]
        eta = eta.rename_axis("axis")
        ov = {"eta2_by_option": _records(eta), "mean_by_state": _records(means)}
        txt = ("Variance of each axis explained by the states (eta², 0 = orthogonal):\n\n" + md(eta)
               + f"\n\nMean of each axis by state ({RECOMMENDED}):\n\n" + md(means))
    else:
        txt = "_No axis columns configured — using the DPD proxy for 'money coming in' only._"
    money = "cred_money_in_points" if "cred_money_in_points" in axes else None
    paid_now = (pd.to_numeric(f[money], errors="coerce") > 0) if money else f.paid_any_3m
    hold = f.state == "stabilized"
    ov["stabilized_vs_money_in"] = {"source": money or "DPD proxy (paid >= 1 month in last 3)",
                                    "stabilized_with_money_in": float(paid_now[hold].mean()) if hold.any() else None,
                                    "others_with_money_in": float(paid_now[~hold].mean())}
    flags = {c: float(pd.to_numeric(f.loc[hold, c], errors="coerce").fillna(0).astype(bool).mean())
             for c in cfg.FLAG_COLS if c in f and f[c].notna().any()}
    ov["stabilized_flagged"] = flags
    R["overlap_other_axes"] = ov
    M.append("## 4. Overlap with the other persona axes\n\n" + txt + "\n\nStabilized vs money coming in:\n\n"
             + md(pd.Series(ov["stabilized_vs_money_in"], name="value").rename_axis("metric").to_frame())
             + ("\n\nShare of stabilized accounts carrying a data flag (frozen bucket, not a payment):\n\n"
                + md(pd.Series(flags, name="share").to_frame()) if flags else ""))

    # ---- backtest: outcomes and stability ----------------------------------------
    bt = None
    if latest_bt is not None and len(latest_bt):
        s2, ok2 = clean_strings(latest_bt.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
        btf = backtest_frame(s2[ok2], k, spine, cfg.EXIT_BUCKET)
        bt = build_features(btf)
        nxt = btf[btf.next_bucket.isin(spine)][["next_string"]].rename(columns={"next_string": "dpd_string"})
        nf = build_features(nxt)
        roll = (bt.next_bucket >= bt.b_now + 1).groupby(bt.b_now).mean()
        R["backtest"] = {"k_months": k, "n_analysed": int(len(bt)),
                         "share_exited_within_k": float(bt.exit_k.mean()),
                         "monthly_roll_rate": {int(b): float(v) for b, v in roll.items()},
                         "scorecards": {}}
        parts = [f"## 5. Backtest — spine as of {k} months ago, outcomes since\n\n"
                 f"{len(bt):,} accounts. Monthly roll rate by bucket (should match the bank's "
                 "~70/80/90/95%):\n\n" + md(roll.rename_axis("bucket").to_frame("roll_rate"))]
        for o, kw in OPTIONS.items():
            card = backtest_scorecard(bt, assign_states(bt, **kw), assign_states(nf, **kw))
            R["backtest"]["scorecards"][o] = _records(card)
            parts.append(f"### {o}\n\n" + md(card))
        M.append("\n\n".join(parts))
    else:
        R["backtest"] = "SKIPPED (no latest-month strings for the backtest population)"
        M.append("## 5. Backtest\n\n_Skipped — no backtest population supplied._")

    # ---- threshold sweeps (on the backtest population when available) ------------
    base, nb = (bt, nf) if bt is not None else (f, None)
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
                     "exit_within_k": base.exit_k[b_].mean() if bt is not None else None})
    sw["epd_max_history"] = rows
    rows = []
    for v in (4, 5, 6):
        st = assign_states(base, stabilized_min_in_band=v)
        h = st == "stabilized"
        rows.append({"stabilized_min_in_band": v, "share": h.mean(),
                     "roll_next_month": (base.next_bucket[h] >= base.b_now[h] + 1).mean() if bt is not None else None,
                     "still_stabilized_next_month": _stay({"stabilized_min_in_band": v}, "stabilized")})
    sw["stabilized_min_in_band"] = rows
    rows = []
    for v in (2, 3, 4):
        st = assign_states(base, **{**OPTIONS[RECOMMENDED], "repeat_min_prior_peak": v})
        rows.append({"repeat_min_prior_peak": v, "share": (st == "repeat_delinquent").mean()})
    sw["repeat_min_prior_peak"] = rows
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
    R["sweeps"] = {kk: [{a: (round(b, 4) if isinstance(b, float) else b) for a, b in r.items()} for r in v]
                   for kk, v in sw.items()}
    M.append("## 6. Threshold sweeps (" + ("backtest population" if bt is not None else "current spine")
             + ")\n\n" + "\n\n".join(f"### {kk}\n\n" + md(pd.DataFrame(v), index=False) for kk, v in sw.items()))

    # ---- residual clustering agreement -------------------------------------------
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    a_states = opts["A_minimal_4"]
    res = ~a_states.isin(["early_payment_default", "stabilized"])
    r = f[res]
    if len(r) > 30_000:
        r = r.sample(30_000, random_state=seed)
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
    M.append("## 7. Clustering the residual (after EPD and stabilized) — agreement (ARI) with "
             "each option\n\n" + md(pd.DataFrame(rows), index=False))

    # ---- shapes and motifs ---------------------------------------------------------
    smp = f.sample(min(len(f), 30_000), random_state=seed)
    shapes = dv.shape_table(smp, label="state", top=20)
    grams = dv.ngram_table(smp, n=4, label="state", top=15)
    R["top_shapes"] = _records(shapes.set_index("shape"))
    R["top_4grams"] = _records(grams.set_index("gram"))
    M.append("## 8. Most common journey shapes and motifs\n\nShapes (N clean, R roll, H hold = paid "
             "one month, P paid 2+ months; run lengths banded):\n\n" + md(shapes, index=False)
             + "\n\n4-grams by lift vs shuffled order:\n\n" + md(grams, index=False))

    return R, "\n\n".join(M)
