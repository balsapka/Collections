"""Deterioration states for the bucket 4–7 spine: a small decision tree, MECE by construction.

Questions are asked in order; the first 'yes' assigns the state. Optional questions are
switched on per option (A / B / C) and never break MECE.

    Q1  Early payment default?  <=3 months of history before this spell (at most one
                                blip inside it, no earlier real spell), run-up to 4
                                took <=3 months                -> early_payment_default
    Q2  Stabilized?             5 of the last 6 months within today's bucket ±1,
                                OR (>= 6 months in buckets 4+ AND at most 1 bucket
                                higher than 6 months ago)      -> stabilized
    Q3  Paying since 4?         [tested, NOT recommended] paid >= half a month's
                                due per month since first reaching 4 -> paying_since_4
    Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3 and cured
                                                               -> repeat_delinquent
    Q5  Straight roller?        run-up (last clean month -> first month at 4) <= 3 months
          yes -> straight_roller   [B, C split: >=12 months of history before the spell
                                    -> straight_roller_seasoned, else straight_roller_early_life]
          no  -> slow_roller       [C split: paid 2+ months at once on the way down
                                    -> slow_roller_erratic, else slow_roller_intermittent]

Code names are stable identifiers; DISPLAY_NAMES / REMARKS carry the business labels.

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
    "epd_max_history": 3,           # months of history before the current spell (blip incl.)
    "epd_max_blips": 1,             # at most one blip (1–2 months at 2, paid off) in that history
    "straight_max_runup": 3,        # months from last clean month to first month at 4
    "stabilized_min_in_band": 5,    # of the last 6 months within today's bucket ±1
    # Long-run clause: an account that has stayed in buckets 4+ for 6 months while rising
    # at most one bucket has paid roughly what was due, even if unevenly (oscillating
    # payers, accounts that just paid down). Straight rollers cannot meet it: they leave
    # the spine within ~4 months. None disables it.
    "stabilized_long_run_months": 6,
    "stabilized_long_run_max_rise": 1,
    # Q3 tested and NOT recommended: unstable (~37% leave it each month), drags the
    # stability of other states to ~90%, barely separates risk, and is mostly the
    # credibility axis's 'money coming in'. Kept only so the test can be repeated.
    "paying_since_4_min_rate": None,  # e.g. 0.5 -> Q3 on
    "repeat_min_prior_peak": None,  # e.g. 3   -> Q4 on (spell counted from bucket 3)
    "seasoned_min_months": None,    # e.g. 12  -> split straight roller (first year on book = early life)
    "split_slow_roller": False,     # True     -> split slow roller by 2+ month payments in run-up
}

OPTIONS = {
    "A_minimal_4": {},
    "B_balanced_6": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12},
    "C_detailed_7": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12, "split_slow_roller": True},
}
RECOMMENDED = "B_balanced_6"

STATE_ORDER = ["early_payment_default", "stabilized", "paying_since_4", "repeat_delinquent",
               "straight_roller", "straight_roller_seasoned", "straight_roller_early_life",
               "slow_roller", "slow_roller_intermittent", "slow_roller_erratic"]
FIXED_STATES = [s for s in STATE_ORDER if s not in ("stabilized", "paying_since_4")]

# Business labels (common card-risk / collections terms). Change freely: code never
# reads these, so renaming for the risk team cannot break the pipeline or old results.
DISPLAY_NAMES = {
    "early_payment_default": "Early payment default (EPD)",
    "stabilized": "Stabilized",
    "paying_since_4": "Paying since bucket 4 (tested, not used)",
    "repeat_delinquent": "Repeat delinquent (re-default)",
    "straight_roller": "Straight roller",
    "straight_roller_seasoned": "Seasoned straight roller",
    "straight_roller_early_life": "Early-life straight roller",
    "slow_roller": "Slow roller (partial payer)",
    "slow_roller_intermittent": "Intermittent payer",
    "slow_roller_erratic": "Erratic payer",
}
REMARKS = {
    "early_payment_default": "Never really paid: defaulted within the first three payments. Called "
                             "'bust-out' internally — but classic bust-out fraud (good history, limit "
                             "build-up, then max-out) shows as a seasoned straight roller and needs a "
                             "fraud overlay on spend data.",
    "stabilized": "The bank's 5-of-6 stabilized rule, plus a long-run clause (6+ months in "
                  "buckets 4+, at most one bucket higher than 6 months ago) so oscillating "
                  "payers and accounts that just paid down are not mislabelled.",
    "paying_since_4": "Rejected — current-behaviour state that belongs to credibility (money coming in).",
    "repeat_delinquent": "Re-default after a cured spell; collections 'recidivism'.",
    "straight_roller": "Rolled through every bucket without paying.",
    "straight_roller_seasoned": "Straight roller after at least a year on book (seasoned).",
    "straight_roller_early_life": "Straight roller in the first year on book (early-life default).",
    "slow_roller": "Paid something on the way down but kept rolling. Also called partial payer.",
    "slow_roller_intermittent": "Slow roller that paid one month here and there.",
    "slow_roller_erratic": "Slow roller that caught up 2+ months at once, then rolled again.",
}


def assign_states(f: pd.DataFrame, **params) -> pd.Series:
    """f: output of features.build_features. Returns one state name per row."""
    p = {**DEFAULTS, **params}
    fast = f.runup_len <= p["straight_max_runup"]
    conds, names = [], []

    def add(cond, name):
        conds.append(cond)
        names.append(name)

    add((f.months_before_spell <= p["epd_max_history"]) & (f.n_blips <= p["epd_max_blips"])
        & (f.n_prior_episodes == 0) & fast, "early_payment_default")
    stab = f.last6_in_band >= p["stabilized_min_in_band"]
    if p["stabilized_long_run_months"] is not None:
        stab |= ((f.months_since_4 >= p["stabilized_long_run_months"])
                 & (f.chg_6m <= p["stabilized_long_run_max_rise"]))
    add(stab, "stabilized")
    if p["paying_since_4_min_rate"] is not None:
        add(f.post4_paid_rate >= p["paying_since_4_min_rate"], "paying_since_4")
    if p["repeat_min_prior_peak"] is not None:
        add(f.max_prior_bucket >= p["repeat_min_prior_peak"], "repeat_delinquent")
    if p["seasoned_min_months"] is not None:
        add(fast & (f.months_before_spell >= p["seasoned_min_months"]), "straight_roller_seasoned")
        add(fast, "straight_roller_early_life")
    else:
        add(fast, "straight_roller")
    if p["split_slow_roller"]:
        add(f.runup_pays >= 1, "slow_roller_erratic")
        default = "slow_roller_intermittent"
    else:
        default = "slow_roller"
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
