"""Deterioration states for the bucket 4–7 spine: a small decision tree, MECE by construction.

Questions are asked in order; the first 'yes' assigns the state. Optional questions are
switched on per option (A / B / C) and never break MECE.

    Q1  Bust-out?        <=6 months of history before this spell, no earlier spell above 2,
                         run-up to 4 took <=3 months                        -> bust_out
    Q2  Holding?         5 of the last 6 months within today's bucket ±1    -> holding
    Q3  Partial payer?   [tested, NOT recommended] paid >= half a month's
                         due per month since first reaching 4               -> partial_payer
    Q4  Relapse?         [B, C] an earlier spell reached bucket 3 and cured -> relapse
    Q5  Fell fast?       run-up (last clean month -> first month at 4) <= 3 months
          yes -> sudden_decline     [B, C split: >=36 months of history before the spell
                                     -> sudden_established, else sudden_early_life]
          no  -> gradual_decline    [C split: paid 2+ months at once on the way down
                                     -> gradual_fought_back, else gradual_slide]

Orthogonality: Q3 (paying now) and Q4 (earlier spell) overlap the payment-credibility
axis (money coming in; pre-delinquency clean), which is why Q3 is off everywhere and Q4
is off in option A. Q1, Q5 and the splits use only the run-up and history length.
Q2 describes current behaviour and moves month to month; every other state is fixed once
the account has passed bucket 4.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULTS = {
    "bust_max_history": 6,          # months of history before the current spell
    "bust_max_prior_peak": 2,       # earlier spells may only have peaked at 2 (paid off from 2)
    "sudden_max_runup": 3,          # months from last clean month to first month at 4
    "hold_min_in_band": 5,          # of the last 6 months within today's bucket ±1
    # Q3 tested and NOT recommended: unstable (~37% leave it each month), drags the
    # stability of other states to ~90%, barely separates risk, and is mostly the
    # credibility axis's 'money coming in'. Kept only so the test can be repeated.
    "partial_min_paid_rate": None,  # e.g. 0.5 -> Q3 on
    "relapse_min_prior_peak": None, # e.g. 3   -> Q4 on (spell counted from bucket 3)
    "established_min": None,        # e.g. 36  -> split sudden
    "split_gradual": False,         # True     -> split gradual by 2+ month payments in run-up
}

OPTIONS = {
    "A_minimal_4": {},
    "B_balanced_6": {"relapse_min_prior_peak": 3, "established_min": 36},
    "C_detailed_7": {"relapse_min_prior_peak": 3, "established_min": 36, "split_gradual": True},
}
RECOMMENDED = "B_balanced_6"

STATE_ORDER = ["bust_out", "holding", "partial_payer", "relapse",
               "sudden_decline", "sudden_established", "sudden_early_life",
               "gradual_decline", "gradual_slide", "gradual_fought_back"]
FIXED_STATES = [s for s in STATE_ORDER if s not in ("holding", "partial_payer")]


def assign_states(f: pd.DataFrame, **params) -> pd.Series:
    """f: output of features.build_features. Returns one state name per row."""
    p = {**DEFAULTS, **params}
    fast = f.runup_len <= p["sudden_max_runup"]
    conds, names = [], []

    def add(cond, name):
        conds.append(cond)
        names.append(name)

    add((f.months_before_spell <= p["bust_max_history"])
        & (f.max_prior_bucket <= p["bust_max_prior_peak"]) & fast, "bust_out")
    add(f.last6_in_band >= p["hold_min_in_band"], "holding")
    if p["partial_min_paid_rate"] is not None:
        add(f.post4_paid_rate >= p["partial_min_paid_rate"], "partial_payer")
    if p["relapse_min_prior_peak"] is not None:
        add(f.max_prior_bucket >= p["relapse_min_prior_peak"], "relapse")
    if p["established_min"] is not None:
        add(fast & (f.months_before_spell >= p["established_min"]), "sudden_established")
        add(fast, "sudden_early_life")
    else:
        add(fast, "sudden_decline")
    if p["split_gradual"]:
        add(f.runup_pays >= 1, "gradual_fought_back")
        default = "gradual_slide"
    else:
        default = "gradual_decline"
    return pd.Series(np.select(conds, names, default), index=f.index)


def order(states) -> list[str]:
    return [s for s in STATE_ORDER if s in set(states)]


def state_scorecard(f: pd.DataFrame, state: pd.Series, state_next: pd.Series | None = None) -> pd.DataFrame:
    """Share, outcome and stability per state. Outcome columns need futures
    (`next_bucket`, `exit_6m`) — present in synthetic data and in real-data backtests."""
    g = f.assign(state=state)
    out = pd.DataFrame({"share": g.state.value_counts(normalize=True)})
    if "next_bucket" in g:
        out["roll_next_month"] = (g.next_bucket >= g.b_now + 1).groupby(g.state).mean()
        out["exit_to_8_in_6m"] = g.groupby("state").exit_6m.mean()
    if state_next is not None:
        same = (state.loc[state_next.index] == state_next)
        out["same_state_next_month"] = same.groupby(state.loc[state_next.index]).mean()
    if "paid_any_3m" in g:
        out["paid_in_last_3m"] = g.groupby("state").paid_any_3m.mean()
        out["earlier_spell"] = (g.n_prior_episodes > 0).groupby(g.state).mean()
    return out.loc[order(out.index)]
