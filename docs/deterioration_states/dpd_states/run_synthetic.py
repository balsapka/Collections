"""METHOD validation on synthetic data: generate a calibrated synthetic spine with planted
patterns, assign the states, and write the evidence report to ../validation/.

    python docs/deterioration_states/run.py synthetic [n_accounts]      # from any folder
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from . import discover as dv
from . import synth
from .features import build_features, encode, _runs
from .states import DEFAULTS, OPTIONS, RECOMMENDED, assign_states, state_scorecard

OUT = Path(__file__).resolve().parents[1] / "validation"   # docs/deterioration_states/validation


def md(df: pd.DataFrame, index: bool = False, floatfmt: str = "{:.2f}") -> str:
    if index:
        df = df.reset_index()
    cells = [[floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in row]
             for row in df.itertuples(index=False)]
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "---|" * len(df.columns)
    return "\n".join([head, sep] + ["| " + " | ".join(r) + " |" for r in cells])


def _spells(s: str, from_bucket: int) -> int:
    b = encode(s)[0]
    return sum(1 for a, e in _runs(b >= 2) if b[a:e].max() >= from_bucket)


def realism(f: pd.DataFrame, st: pd.Series) -> str:
    rr = synth.roll_rates(f)
    one3 = (f.dpd_string.map(lambda s: _spells(s, 3)) == 1).mean()
    one4 = (f.dpd_string.map(lambda s: _spells(s, 4)) == 1).mean()
    bust = (st == "early_payment_default").mean()
    stab = ((f.last6_in_band >= 5) & (st != "early_payment_default")).mean()
    stab_clause = (st == "stabilized").mean()
    rows = [(f"Monthly roll rate at {b}", f"{synth.ROLL_TARGET[b]:.0%}", f"{rr[b]:.0%}") for b in synth.SPINE]
    rows += [
        ("One spell only (spell from bucket 3)", "~85%", f"{one3:.0%}"),
        ("One spell only (spell from bucket 4)", "~85%", f"{one4:.0%}"),
        ("EPD ('bust-out') share", "6%", f"{bust:.1%}"),
        ("Stabilized share (your 5/6 rule, after EPD)", "6%", f"{stab:.1%}"),
        ("Stabilized share incl. long-run clause", "—", f"{stab_clause:.1%}"),
        ("Never paid since reaching 4", "majority (90% 'overkill')", f"{1 - f.paid_after_4_so_far.mean():.0%}"),
    ]
    t = pd.DataFrame(rows, columns=["check", "your book", "synthetic"])
    mix = f.b_now.value_counts(normalize=True).sort_index().rename("share").to_frame()
    ten = pd.cut(f.months_before_spell, [-1, 3, 6, 12, 24, 36, 60, 120, 999],
                 labels=["0-3", "4-6", "7-12", "13-24", "25-36", "37-60", "61-120", "121+"])
    ten = ten.value_counts(normalize=True).sort_index().rename("share").to_frame()
    dq = pd.DataFrame([
        ("accounts with a payment holiday in history", f"{f.had_holiday.mean():.1%}"),
        ("accounts with a +2 jump repaired (next to a hold)", f"{(f.n_jumps_repaired > 0).mean():.1%}"),
        ("accounts with a +2 jump left (read as roll)", f"{(f.n_jumps_left > 0).mean():.1%}"),
    ], columns=["data-quality effect", "share"])
    return ("## A. Is the synthetic spine life-like?\n\n" + md(t)
            + "\n\nCurrent bucket mix:\n\n" + md(mix, index=True, floatfmt="{:.0%}")
            + "\n\nMonths of history before the current spell (continuous — no planted gaps):\n\n"
            + md(ten, index=True, floatfmt="{:.0%}") + "\n\n" + md(dq))


def sweep(f: pd.DataFrame, nx: pd.DataFrame) -> str:
    out = ["## D. Threshold sweeps (one parameter at a time, others at default)"]
    planted = f.true_archetype

    rows = []
    for v in (2, 3, 4, 6, 9, 12):
        s = assign_states(f, epd_max_history=v)
        b = s == "early_payment_default"
        rows.append({"epd_max_history": v, "epd_share": b.mean(), "exit_6m": f.exit_6m[b].mean(),
                     "planted_bustouts_caught": b[planted == "bust_out"].mean(),
                     "share_of_state_planted_bustout": (planted[b] == "bust_out").mean()})
    out.append("### Q1 early payment default (EPD) — months of history before the spell\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for band in (4, 5, 6):
        s = assign_states(f, stabilized_min_in_band=band)
        h = s == "stabilized"
        s2 = assign_states(nx, stabilized_min_in_band=band)
        held = h.loc[nx.index]
        rows.append({"min_in_band (of 6)": band, "stabilized_share": h.mean(),
                     "roll_next_month": (f.next_bucket[h] >= f.b_now[h] + 1).mean(),
                     "exit_6m": f.exit_6m[h].mean(),
                     "still_stabilized_next_month": (s2[held[held].index] == "stabilized").mean(),
                     "payment_holiday_share": f.had_holiday[h].mean(),
                     "planted_stabilizers_caught": h[planted == "stabilized"].mean()})
    out.append("### Q2 stabilized — months within today's bucket ±1 (of the last 6)\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for v in (0.34, 0.5, 0.67):
        kw = {**OPTIONS["C_detailed_7"], "paying_since_4_min_rate": v}
        s, s2 = assign_states(f, **kw), assign_states(nx, **kw)
        m = s == "paying_since_4"
        mm = m.loc[nx.index]
        others = ~s.isin(["stabilized", "paying_since_4"])
        rows.append({"paying_since_4_min_rate": v, "share": m.mean(),
                     "roll_next_month": (f.next_bucket[m] >= f.b_now[m] + 1).mean(),
                     "still_paying_since_4_next_month": (s2[mm[mm].index] == "paying_since_4").mean(),
                     "paid_in_last_3m": f.paid_any_3m[m].mean(),
                     "stability_of_other_states": (s.loc[nx.index][others.loc[nx.index]]
                                                   == s2[others.loc[nx.index]]).mean()})
    out.append("### Q3 paying since 4 (tested, not recommended) — months paid per month since 4\n\n"
               + md(pd.DataFrame(rows)))

    rows = []
    for v in (2, 3, 4):
        s = assign_states(f, **{**OPTIONS[RECOMMENDED], "repeat_min_prior_peak": v})
        rows.append({"earlier spell reached bucket": v, "repeat_share": (s == "repeat_delinquent").mean()})
    out.append("### Q4 repeat delinquent — how deep the earlier spell must have gone\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for v in (3, 4, 5):
        s = assign_states(f, straight_max_runup=v)
        g = s == "slow_roller"
        rows.append({"straight_max_runup": v, "straight_share": (s == "straight_roller").mean(),
                     "slow_share": g.mean(),
                     "slow_slides_in_slow_roller": g[planted == "slow_slide"].mean(),
                     "abrupt_in_straight": (s[planted == "clean_abrupt_shock"] == "straight_roller").mean()})
    out.append("### Q5 straight vs slow roller — max run-up months\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for v in (12, 18, 24, 36):
        s = assign_states(f, **{**OPTIONS[RECOMMENDED], "seasoned_min_months": v})
        rows.append({"seasoned_min_months": v, "seasoned": (s == "straight_roller_seasoned").mean(),
                     "early_life": (s == "straight_roller_early_life").mean()})
    out.append("### Q5 split — months of history before the spell (seasoned vs early-life straight roller)\n\n"
               + md(pd.DataFrame(rows)))
    return "\n\n".join(out)


RESIDUAL_FEATURES = ["months_before_spell", "n_blips", "n_prior_episodes", "max_prior_bucket",
                     "clean_gap_before_current", "runup_len", "runup_holds", "runup_pays",
                     "post4_paid_rate", "rec_paid_rate"]


def residual_clusters(f: pd.DataFrame, options: dict[str, pd.Series]) -> str:
    """Cluster only what is left after EPD and stabilized, and see which option's
    residual states the natural groups agree with."""
    base = assign_states(f)
    res = ~base.isin(["early_payment_default", "stabilized"])
    r = f[res]
    X = r[RESIDUAL_FEATURES].astype(float).copy()
    for c in ("months_before_spell", "clean_gap_before_current", "runup_len"):
        X[c] = np.log1p(X[c])
    X = StandardScaler().fit_transform(X)
    smp = np.random.default_rng(7).choice(len(X), size=min(4000, len(X)), replace=False)
    rows, fits = [], {}
    for k in range(2, 9):
        lab = KMeans(k, n_init=10, random_state=7).fit_predict(X)
        boot = KMeans(k, n_init=10, random_state=3).fit(X[np.random.default_rng(3).choice(len(X), len(X))]).predict(X)
        fits[k] = lab
        rows.append({"k": k, "silhouette": silhouette_score(X[smp], lab[smp]),
                     "bootstrap_ARI": adjusted_rand_score(lab, boot),
                     **{f"agree_{o}": adjusted_rand_score(lab, s[res]) for o, s in options.items()}})
    g = r.assign(c=fits[6]).groupby("c")
    prof = pd.DataFrame({
        "share_of_spine": g.size() / len(f),
        "median_months_before_spell": g.months_before_spell.median(),
        "earlier_spell_to_3+": g.max_prior_bucket.apply(lambda x: (x >= 3).mean()),
        "straight_runup": g.runup_len.apply(lambda x: (x <= 3).mean()),
        "held_on_way": g.runup_holds.apply(lambda x: (x > 0).mean()),
        "paid_2+_on_way": g.runup_pays.apply(lambda x: (x > 0).mean()),
        "median_paid_rate_since_4": g.post4_paid_rate.median(),
        "top_state_option_C": g.apply(lambda x: options["C_detailed_7"][x.index].value_counts().index[0]),
    }).sort_values("share_of_spine", ascending=False)
    return ("## C. Clustering the residual (after EPD and stabilized)\n\n"
            f"Residual = {res.mean():.0%} of the spine. Agreement (ARI) between k-means clusters and each "
            "option's residual states:\n\n" + md(pd.DataFrame(rows), floatfmt="{:.2f}")
            + "\n\nk = 6 cluster profiles:\n\n" + md(prof, index=True))


def discovery(f: pd.DataFrame) -> str:
    out = [f"## E. Discovery views (states = {RECOMMENDED})"]
    st = dv.shape_table(f, label="state", top=15)
    out.append(f"### Top 15 shapes ({f.dpd_string.map(dv.shape).nunique()} distinct) — by state\n\n" + md(st))
    ng = dv.ngram_table(f, n=4, label="state")
    out.append("### 4-grams ranked by lift vs shuffled order (support ≥ 1%)\n\n" + md(ng))
    X = dv.cluster_matrix(f)
    sample = np.random.default_rng(7).choice(len(X), size=min(4000, len(X)), replace=False)
    rows = []
    for k in (4, 5, 6, 7, 8):
        lab = KMeans(k, n_init=10, random_state=7).fit_predict(X)
        boots = [KMeans(k, n_init=5, random_state=s).fit(X[np.random.default_rng(s).choice(len(X), len(X))]).predict(X)
                 for s in (1, 2)]
        rows.append({"k": k, "silhouette": silhouette_score(X[sample], lab[sample]),
                     "bootstrap_ARI": adjusted_rand_score(*boots),
                     "ARI_vs_planted": adjusted_rand_score(f.true_archetype, lab),
                     "ARI_vs_states": adjusted_rand_score(f.state, lab)})
    out.append("### k-means on clock-safe features\n\n" + md(pd.DataFrame(rows), floatfmt="{:.3f}"))
    return "\n\n".join(out)


def main(n: int = 20_000) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    synth.calibrate()
    df = synth.generate(n)
    f = build_features(df)
    nx_in = df[df.next_bucket.between(4, 7)][["next_string"]].rename(columns={"next_string": "dpd_string"})
    nx = build_features(nx_in)
    opts = {o: assign_states(f, **kw) for o, kw in OPTIONS.items()}
    opts_next = {o: assign_states(nx, **kw) for o, kw in OPTIONS.items()}
    f["state"] = opts[RECOMMENDED]
    sec = [realism(f, opts["A_minimal_4"])]

    # B. the three options
    parts = ["## B. State options — each a MECE tree (first 'yes' wins)\n\n"
             f"Shared thresholds: `{DEFAULTS}`"]
    for o, kw in OPTIONS.items():
        s = opts[o]
        assert s.notna().all()
        card = state_scorecard(f, s, opts_next[o])
        parts.append(f"### {o} — {s.nunique()} states (extra switches: `{kw}`)\n\n" + md(card, index=True))
    c = opts["C_detailed_7"]
    parts.append("Option C — state mix by current bucket:\n\n"
                 + md(pd.crosstab(c, f.b_now, normalize="columns"), index=True)
                 + "\n\nOption C — planted pattern → state (row share):\n\n"
                 + md(pd.crosstab(f.true_archetype, c, normalize="index"), index=True))
    ex = (f.assign(state_c=c).groupby("state_c").sample(3, random_state=1)[["state_c", "dpd_string"]]
          .assign(oldest_to_newest=lambda x: x.dpd_string.str[::-1].str[-30:]))
    parts.append("Option C — examples (last 30 months, oldest → newest):\n\n" + md(ex[["state_c", "oldest_to_newest"]]))
    sec.append("\n\n".join(parts))

    sec.append(residual_clusters(f, opts))
    sec.append(sweep(f, nx))

    sec.append(discovery(f))

    report = (f"# DPD deterioration states — synthetic validation {ts}\n\n"
              f"{n:,} calibrated synthetic spine accounts (current bucket 4–7). "
              "Strings: leftmost = current bucket. 0 ≡ 1.\n\n" + "\n\n".join(sec) + "\n")
    OUT.mkdir(exist_ok=True)
    path = OUT / f"dpd_states_validation_{ts}.md"
    path.write_text(report)
    print(path)
    return path


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20_000)
