"""Deterioration states for the bucket 4–7 spine: a small decision tree, MECE by construction.

Questions are asked in order; the first 'yes' assigns the state. Optional questions are
switched on per option (A / B / C) and never break MECE.

    Q0  Journey start observed?   the OLDEST OBSERVED month is already at bucket 2+ (a spell
                                older than the window / floor, a restructured account
                                re-opened at its old bucket, migrated or missing history):
                                how the account fell in is not visible, so every
                                fall-in state would be a guess. Stabilized needs only
                                the last 6 months, so it is still assigned; otherwise
                                                               -> unknown
    Q1  Early payment default?  <=3 months of history before this spell (at most one
                                blip inside it, no earlier real spell) AND never paid
                                since crossing bucket 2: every month of the spell a
                                roll, still falling; and the string was not cropped (it
                                must start at the first billed month) -> early_payment_default
    Q2  Stabilized?             today's bucket <= 7 (151-180 DPD; RL <= 6) — never at 180+ —
                                AND 5 of the last 6 months within
                                today's bucket ±1, OR (>= 6 months since first reaching 4
                                AND at most 1 bucket higher than 6 months ago) -> stabilized
    Q3  Paying since 4?         [tested, NOT recommended] paid >= half a month's
                                due per month since first reaching 4 -> paying_since_4
    Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3, cured, and
                                ended within 12 months before this spell started
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
Q2 describes current behaviour and moves month to month; EPD ends the month the account
pays; every other state is fixed once the account has passed bucket 4 (it can only move
into stabilized).

Parameters marked [business] are agreed business definitions: change them only with the
business owner — never to make a share or an expectation check come out right.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULTS = {
    "epd_max_history": 3,           # [business] months of history before the spell (blip incl.)
    "epd_max_blips": 1,             # [business] at most one blip (1–2 months at 2, paid off)
    "straight_max_runup": 3,        # months from last clean month to first month at 4
    "stabilized_min_in_band": 5,    # [business] of the last 6 months within today's bucket ±1
    # [business] Long-run clause: an account 6+ months past first reaching 4 that has risen
    # at most one bucket in 6 months has paid roughly what was due, even if unevenly
    # (oscillating payers, accounts that just paid down). Straight rollers cannot meet it:
    # they leave the spine within ~4 months. None disables it.
    "stabilized_long_run_months": 6,
    "stabilized_long_run_max_rise": 1,
    # Q3 tested and NOT recommended: unstable (~37% leave it each month), drags the
    # stability of other states to ~90%, barely separates risk, and is mostly the
    # credibility axis's 'money coming in'. Kept only so the test can be repeated.
    "paying_since_4_min_rate": None,  # e.g. 0.5 -> Q3 on
    "repeat_min_prior_peak": None,  # [business] e.g. 3 -> Q4 on (earlier spell reached 3)
    "repeat_window_months": 12,     # [business] earlier spell ended <= 12 months before this one
    "seasoned_min_months": None,    # [business] e.g. 12 -> split straight roller (first year = early life)
    "split_slow_roller": False,     # True -> split slow roller by 2+ month payments in run-up
    # [business] Stabilized only up to bucket 7 (151-180 DPD; RL 6): never in the 180+
    # segment, where a hold at the ceiling is not a payment.
    "stabilized_max_bucket": 7,
}

OPTIONS = {
    "A_minimal_4": {},
    "B_balanced_6": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12},
    "C_detailed_7": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12, "split_slow_roller": True},
}
RECOMMENDED = "B_balanced_6"

STATE_ORDER = ["unknown", "early_payment_default", "stabilized", "paying_since_4",
               "repeat_delinquent", "straight_roller", "straight_roller_seasoned",
               "straight_roller_early_life", "slow_roller", "slow_roller_intermittent",
               "slow_roller_erratic"]
# States that never change once the account is past bucket 4 (how they fell in). EPD is
# not one of them: it ends the month the account pays. Stabilized / paying_since_4 describe
# current behaviour. A fixed state may legitimately move INTO stabilized.
FIXED_STATES = [s for s in STATE_ORDER
                if s not in ("unknown", "early_payment_default", "stabilized", "paying_since_4")]
CURRENT_STATES = ["stabilized", "paying_since_4"]

# Business labels (common card-risk / collections terms). Change freely: code never
# reads these, so renaming for the risk team cannot break the pipeline or old results.
DISPLAY_NAMES = {
    "unknown": "Unknown — start of the delinquency journey not observed",
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
    "unknown": "The oldest observed month is already delinquent, so how the account fell in "
               "is not visible: a spell older than the history window / floor (common at 180+), "
               "a restructured card/loan re-opened at its old bucket, a migrated account or "
               "missing history. Stabilized is still assigned (it needs only the last 6 months).",
    "early_payment_default": "Never paid since crossing bucket 2 and still falling, at most 3 months "
                             "after the first bill. Called 'bust-out' internally — but classic bust-out "
                             "fraud (good history, limit build-up, then max-out) shows as a seasoned "
                             "straight roller and needs a fraud overlay on spend data.",
    "stabilized": "The bank's 5-of-6 stabilized rule, plus a long-run clause (6+ months since "
                  "first reaching 4, at most one bucket higher than 6 months ago) so oscillating "
                  "payers and accounts that just paid down are not mislabelled.",
    "paying_since_4": "Rejected — current-behaviour state that belongs to credibility (money coming in).",
    "repeat_delinquent": "Re-default within 12 months of curing a spell that reached bucket 3; "
                         "collections 'recidivism'.",
    "straight_roller": "Rolled straight to bucket 4 (no payment on the way down). Describes how "
                       "they fell in — some have paid since.",
    "straight_roller_seasoned": "Rolled straight to bucket 4 after at least a year on book (seasoned).",
    "straight_roller_early_life": "Rolled straight to bucket 4 in the first year on book (early-life default).",
    "slow_roller": "Paid something on the way down to bucket 4 but kept rolling. Also called partial payer.",
    "slow_roller_intermittent": "Slow roller that paid one month here and there on the way down.",
    "slow_roller_erratic": "Slow roller that caught up 2+ months at once on the way down, then rolled again.",
}


def option_states(option: str) -> list[str]:
    """Every state an option can produce (for share tables that must show empty states)."""
    p = {**DEFAULTS, **OPTIONS[option]}
    out = ["unknown", "early_payment_default", "stabilized"]
    out += ["paying_since_4"] if p["paying_since_4_min_rate"] is not None else []
    out += ["repeat_delinquent"] if p["repeat_min_prior_peak"] is not None else []
    out += (["straight_roller_seasoned", "straight_roller_early_life"]
            if p["seasoned_min_months"] is not None else ["straight_roller"])
    out += (["slow_roller_erratic", "slow_roller_intermittent"] if p["split_slow_roller"]
            else ["slow_roller"])
    return order(out)


def assign_states(f: pd.DataFrame, **params) -> pd.Series:
    """f: output of features.build_features. Returns one state name per row."""
    p = {**DEFAULTS, **params}
    fast = f.runup_len <= p["straight_max_runup"]
    conds, names = [], []

    def add(cond, name):
        conds.append(cond)
        names.append(name)

    # cropped to the reliable window: the oldest digit is not the first billed month
    cropped = f["history_truncated"].astype(bool) if "history_truncated" in f else False
    stab = (f.last6_in_band >= p["stabilized_min_in_band"])
    if p["stabilized_long_run_months"] is not None:
        stab |= ((f.months_since_4 >= p["stabilized_long_run_months"])
                 & (f.chg_6m <= p["stabilized_long_run_max_rise"]))
    stab &= f.b_now <= p["stabilized_max_bucket"]
    add(f.starts_delinquent & stab, "stabilized")
    add(f.starts_delinquent, "unknown")
    add((f.months_before_spell <= p["epd_max_history"]) & (f.n_blips <= p["epd_max_blips"])
        & (f.n_prior_episodes == 0) & (f.spell_pay_events == 0) & ~cropped, "early_payment_default")
    add(stab, "stabilized")
    if p["paying_since_4_min_rate"] is not None:
        add(f.post4_paid_rate >= p["paying_since_4_min_rate"], "paying_since_4")
    if p["repeat_min_prior_peak"] is not None:
        gap = f[f"gap_prior_peak{min(max(int(p['repeat_min_prior_peak']), 2), 4)}"]
        add(gap <= p["repeat_window_months"], "repeat_delinquent")
    if p["seasoned_min_months"] is not None:
        # a cropped string means the account is older than the window: seasoned
        add(fast & ((f.months_before_spell >= p["seasoned_min_months"]) | cropped), "straight_roller_seasoned")
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
