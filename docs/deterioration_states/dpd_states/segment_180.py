"""PROTOTYPE — deterioration states for the 180+ segment (current bucket 8 or 9; 9 is the cap).

At 9 the string cannot show payments (paying one month or nothing both read 9 9 9), so
there is no 'stabilized'. The states describe how the account fell in, plus two signals
that only exist at 180+, plus an honest state when the path in is outside the window:

    Q1  Paying in default?     dropped below 9 after first reaching it (paid several
                               months at once)                    -> paying_in_default
    Q1b Stabilized?            below the cap (CC 8 only; never at 9, never RL 7) and the
                               spine's stabilized rule holds      -> stabilized
    Q2  Broken payer?          was stabilized (bank's 5-of-6 rule) for 6+ months while in
                               buckets 4–7, then rolled on to 9 (visible even when the
                               run-up is not)                     -> broken_payer
    Q0  Journey start observed? the oldest observed month is already delinquent (incl.
                               every month at 8 or 9): how it fell in is not visible
                                                                  -> unknown
    Q3  Early payment default? <=3 months on book before the spell (<=1 blip), no earlier
                               spell, no payment between bucket 2 and reaching 9
                                                                  -> early_payment_default
    Q4  Repeat delinquent?     earlier spell reached 3, cured, ended <=12 months before
                                                                  -> repeat_delinquent
    Q5  Straight roller?       run-up to 4 took <=3 months: seasoned (>=12 months on book,
                               or history cropped by the window = older than it) /
                               early-life; otherwise              -> slow_roller

Plus an attribute, not a state: time in default (months since first reaching 8), banded.

    python docs/deterioration_states/run.py s180            # synthetic run, three time-at-9 scenarios
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import synth
from .analysis import crop_history, md
from .features import _runs, build_features, encode

DEFAULT_TOP = 9
from .config import MAX_HISTORY_MONTHS as WINDOW   # reliable history window (32 months)


# --- synthetic 180+ lifecycles -----------------------------------------------------------

def _to_default(path: list[int], rng, median_months_at_9: float) -> tuple[list[int], str]:
    """Continue a lifecycle that reached 8 into the 180+ segment: 9, then months at 9 until
    write-off / end of observation, with rare 'paying in default' events."""
    tag = ""
    path.append(DEFAULT_TOP)
    months = int(np.clip(rng.gamma(1.5, median_months_at_9 / 1.2), 1, 96))
    for _ in range(months):
        if rng.random() < 0.012:                     # paid several months at once
            drop = int(rng.integers(1, 4))
            path.append(DEFAULT_TOP - drop)
            tag = "paid_in_default"
            while path[-1] < DEFAULT_TOP:            # rolls back up unless it keeps paying
                path.append(path[-1] + 1)
        else:
            path.append(DEFAULT_TOP)
    return path, tag


def _broken_payer(rng) -> list[int]:
    """Stabilized for a long time in 4–7, then the arrangement / capacity broke: rolls to 9."""
    path = synth._normal(rng, synth._tenure(rng, lo=6))
    synth._roll_to(path, int(rng.choice([4, 5, 6], p=[0.6, 0.3, 0.1])))
    for _ in range(int(rng.integers(8, 30))):
        b, u = path[-1], rng.random()
        path.append(b if u < 0.8 else (b + 1 if u < 0.9 and b < 7 else max(b - 1, 4)))
    synth._roll_to(path, 8)
    return path


def generate_180(n: int = 20_000, median_months_at_9: float = 12, seed: int = 7,
                 share_no_history: float = 0.03) -> pd.DataFrame:
    """Snapshot of the 180+ segment: accounts whose current bucket is 8 or 9, sampled in
    proportion to the months they spend there, history cropped to the reliable window."""
    rng = np.random.default_rng(seed)
    names = list(synth.ARCHETYPES) + ["broken_payer"]
    w = np.array([synth.ARCHETYPES[k][0] for k in synth.ARCHETYPES] + [0.03])
    pool_names = rng.choice(names, size=4 * n, p=w / w.sum())
    pool, tags = [], []
    for k in pool_names:
        p = _broken_payer(rng) if k == "broken_payer" else synth.ARCHETYPES[k][1](rng)
        if p[-1] < 8:                                # lifecycle ended before 180+ (cure / settle)
            synth._roll_to(p, 8)
        p = p[:next(i for i, x in enumerate(p) if x >= 8) + 1]
        p, tag = _to_default(p, rng, median_months_at_9)
        pool.append(p)
        tags.append(tag)
    months = np.array([sum(1 for x in p if x >= 8) for p in pool], dtype=float)
    chosen = rng.choice(len(pool), size=n, replace=False, p=months / months.sum())
    rows = []
    for j in chosen:
        p = pool[j]
        t = int(rng.choice([i for i, x in enumerate(p) if x >= 8]))
        hist = p[:t + 1]
        label = pool_names[j]
        if DEFAULT_TOP in hist and min(hist[hist.index(DEFAULT_TOP):]) < DEFAULT_TOP:
            label = "paid_in_default"                # the payment is visible in this snapshot
        rows.append({"dpd_string": "".join(map(str, reversed(hist))), "planted": label})
    df = pd.DataFrame(rows)
    nh = rng.random(len(df)) < share_no_history          # migrated / no history: all 9s
    df.loc[nh, "dpd_string"] = df.loc[nh, "dpd_string"].map(lambda s: "9" * min(len(s), int(rng.integers(3, 25))))
    df.loc[nh, "planted"] = "no_history"
    return df


# --- 180+ features and states -------------------------------------------------------------

def features_180(df: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    s, cropped = crop_history(df.dpd_string, window)
    f = build_features(df.assign(dpd_string=s, history_truncated=cropped))
    extra = []
    for x in f.dpd_string:
        b, d, c = encode(x)
        sp0 = _runs(b >= 2)[-1][0]
        first8 = int(np.argmax(b >= 8))
        first9 = int(np.argmax(b >= 9)) if (b >= 9).any() else None
        # payment events from spell start until first reaching 9 (holds at the cap are not payments)
        upto = (first9 if first9 is not None else len(b) - 1)
        pre9 = c[max(sp0 - 1, 0):upto]
        after9 = d[first9:] if first9 is not None else np.array([])
        # was stabilized (bank rule: 5 of 6 within ±1) at some month while in 4–7, for 6+ months
        stab_months = 0
        for t in range(sp0, first8):
            if 4 <= b[t] <= 7 and t >= 5 and (np.abs(b[t - 5:t + 1] - b[t]) <= 1).sum() >= 5:
                stab_months += 1
        extra.append({"all_default": bool(set(x) <= {"8", "9"}),
                      "months_in_default": len(b) - 1 - first8,
                      "default_left_censored": first8 == 0,
                      "pay_events_before_9": int((pre9 != 1).sum()),
                      "paid_in_default": bool((after9 < 0).any()),
                      "stabilized_months_in_4_7": stab_months})
    return pd.concat([f, pd.DataFrame(extra, index=f.index)], axis=1)


def assign_180(f: pd.DataFrame, seasoned_min_months: int = 12, repeat_window: int = 12,
               cap_bucket: int = DEFAULT_TOP) -> pd.Series:
    fast = f.runup_len <= 3
    stab = ((f.last6_in_band >= 5) | ((f.months_since_4 >= 6) & (f.chg_6m <= 1))) & (f.b_now < cap_bucket)
    conds = [
        f.paid_in_default,
        stab,                                       # CC 8 only: 9 is the cap
        f.stabilized_months_in_4_7 >= 6,            # visible even when the run-up is not
        f.starts_delinquent,                        # includes all_default
        (f.months_before_spell <= 3) & (f.n_blips <= 1) & (f.n_prior_episodes == 0)
        & (f.pay_events_before_9 == 0) & ~f.history_truncated,
        f.gap_prior_peak3 <= repeat_window,
        # cropped = older than the window, so on book well over a year: seasoned
        fast & ((f.months_before_spell >= seasoned_min_months) | f.history_truncated),
        fast,
    ]
    names = ["paying_in_default", "stabilized", "broken_payer", "unknown", "early_payment_default",
             "repeat_delinquent", "straight_roller_seasoned", "straight_roller_early_life"]
    return pd.Series(np.select(conds, names, "slow_roller"), index=f.index)


def default_band(f: pd.DataFrame) -> pd.Series:
    m = f.months_in_default
    return pd.Series(np.select([f.default_left_censored, m < 6, m < 12],
                               [f"{WINDOW - 1}+ (since before window)", "0–5", "6–11"], "12+"),
                     index=f.index)


ORDER = ["paying_in_default", "stabilized", "broken_payer", "unknown", "early_payment_default",
         "repeat_delinquent", "straight_roller_seasoned", "straight_roller_early_life", "slow_roller"]


def main(n: int = 20_000) -> None:
    synth.calibrate(n=6000, iters=5)
    for med in (6, 12, 24):
        df = generate_180(n, median_months_at_9=med)
        f = features_180(df)
        st = assign_180(f).rename("state")
        band = default_band(f).rename("time_in_default")
        share = st.value_counts(normalize=True).reindex(ORDER).fillna(0).rename("share")
        print(f"\n=== typical (median) time at 9 = {med} months · {len(df):,} accounts · window {WINDOW} ===")
        print(md(share.to_frame()))
        print("\nTime in default (months since first reaching 8):\n")
        print(md(band.value_counts(normalize=True).rename("share").to_frame()))
        if med == 12:
            print("\nState × time in default (row shares):\n")
            print(md(pd.crosstab(st, band, normalize="index").reindex(ORDER).dropna(how="all")))
            print("\nPlanted pattern → state (row shares):\n")
            print(md(pd.crosstab(df.planted, st, normalize="index")[[c for c in ORDER if c in set(st)]]))
