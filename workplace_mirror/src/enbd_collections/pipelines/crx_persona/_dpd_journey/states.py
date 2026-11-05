"""The A4 state tree (METHODOLOGY.md option B): ONE tree for 60-180 and 180+.

Rules Q0-Q4 and the thresholds in ``STATE_RULES`` follow the methodology; the code
differs in D1 (Q0 needs history_blind) and D2 (restructured accounts are
history_blind), see specs/A4_deterioration_conformance.md.
"""

from __future__ import annotations

from typing import Any

from .core import journey_features

STATE_RULES = {
    "epd_max_history": 3,  # Q1 [business] months of history before the spell (+ blip)
    "epd_max_blips": 1,  # Q1 [business]
    "straight_max_runup": 3,  # Q4 last clean month -> first month at 4
    "stabilized_min_in_band": 5,  # Q2 [business] of last 6 months in today's bucket ±1
    "stabilized_long_run_months": 6,  # Q2 [business]
    "stabilized_long_run_max_rise": 1,  # Q2 [business]
    # Q2 [business] canonical: CC 7 / RL 6 = 151-180 DPD. Never at 180+.
    "stabilized_max_bucket": 7,
    "repeat_min_prior_peak": 3,  # Q3 [business] earlier spell reached bucket 3 ...
    "repeat_window_months": 12,  # Q3 [business] ... and ended <= 12 months before
    "seasoned_min_months": 12,  # Q4 [business] months on book before the spell
}

STATES = [
    "unknown",
    "early_payment_default",
    "stabilized",
    "repeat_delinquent",
    "straight_roller_seasoned",
    "straight_roller_early_life",
    "slow_roller",
]

DISPLAY_NAMES = {
    "unknown": "Unknown — start of the delinquency journey not observed",
    "early_payment_default": "Early payment default (EPD)",
    "stabilized": "Stabilized",
    "repeat_delinquent": "Repeat delinquent",
    "straight_roller_seasoned": "Seasoned straight roller",
    "straight_roller_early_life": "Early-life straight roller",
    "slow_roller": "Slow roller (partial payer)",
}


def _is_stabilized(f: dict[str, Any]) -> bool:
    """Q2: 60-180 only, five of the last six months within today's bucket +-1, or a long
    run since first reaching 4 that has risen by at most one bucket."""
    p = STATE_RULES
    return f["b_now"] <= p["stabilized_max_bucket"] and (
        f["last6_in_band"] >= p["stabilized_min_in_band"]
        or (
            f["months_since_4"] >= p["stabilized_long_run_months"]
            and f["chg_6m"] <= p["stabilized_long_run_max_rise"]
        )
    )


def _is_early_payment_default(f: dict[str, Any], history_blind: bool) -> bool:
    """Q1: the spell follows a short, clean history, with no payment in it."""
    p = STATE_RULES
    return (
        f["months_before_spell"] <= p["epd_max_history"]
        and f["n_blips"] <= p["epd_max_blips"]
        and f["n_prior_episodes"] == 0
        and f["spell_pay_events"] == 0
        and not history_blind
    )


def _is_repeat_delinquent(f: dict[str, Any]) -> bool:
    """Q3: an earlier spell reached the peak bucket and ended within the window."""
    return f["gap_prior_peak3"] <= STATE_RULES["repeat_window_months"]


def _is_straight_roller(f: dict[str, Any]) -> bool:
    """Q4: the run-up to bucket 4 took at most `straight_max_runup` months."""
    return f["runup_len"] <= STATE_RULES["straight_max_runup"]


# pylint: disable-next=too-many-return-statements
def assign_state(
    f: dict[str, Any], cropped: bool, restructure_blind_spot: bool = False
) -> str:
    """One state per account, same tree and vocabulary in both segments. First 'yes' wins.

    Q0 journey start not observed (oldest observed month delinquent AND history_blind —
                             history before the window is genuinely missing, or this
                             account is a restructured entry whose predecessor contract's
                             history is invisible) -> stabilized if Q2, else unknown
    Q1 early payment default <=3 months before the spell, <=1 blip, no earlier spell, no payment
                             in the spell (holds at the ceiling are not payments), not
                             history_blind
    Q2 stabilized            60-180 only (today <= CC 7 / RL 6): 5 of the last 6 months within
                             today's bucket ±1, or >=6 months since first reaching 4 and at most
                             1 bucket higher than 6 months ago
    Q3 repeat delinquent     an earlier spell reached 3, cured, ended <=12 months before this one
    Q4 straight roller       run-up to 4 took <=3 months: seasoned (>=12 months on book, or
                             history_blind = older than the window / restructured) / early life
    else slow roller
    """
    p = STATE_RULES
    # history_blind = the journey start is not observed: a Stage-1 crop (floor date,
    # unresolvable gap, dataset edge) or a restructured account, whose first row is a
    # fresh contract and not a fresh delinquency (conformance D1, D2). A CC account
    # cannot start its first billing cycle delinquent; an RL loan can (native bucket 1,
    # first EMI missed), so a delinquent start alone is not blindness.
    history_blind = cropped or restructure_blind_spot
    # Q2 stabilized — computed up front: both Q0 and the main sequence below consult it.
    stab = _is_stabilized(f)
    # Q0 fires only when history_blind; with the whole journey observed a delinquent
    # oldest month is a real start, so fall through to the normal cascade.
    if f["starts_delinquent"] and history_blind:
        return "stabilized" if stab else "unknown"
    if _is_early_payment_default(f, history_blind):  # Q1
        return "early_payment_default"
    if stab:  # Q2
        return "stabilized"
    if _is_repeat_delinquent(f):  # Q3
        return "repeat_delinquent"
    if _is_straight_roller(f):  # Q4
        if f["months_before_spell"] >= p["seasoned_min_months"] or history_blind:
            return "straight_roller_seasoned"
        return "straight_roller_early_life"
    return "slow_roller"


def classify(  # pylint: disable=too-many-positional-arguments
    buckets_native: list[int],
    cropped: bool,
    offset: int,
    canon_top: int,
    repair: bool = True,
    restructure_blind_spot: bool = False,
) -> dict:
    """Features + state for one account (native buckets, oldest -> newest)."""
    f = journey_features(
        [max(x + offset, 1) for x in buckets_native], canon_top, repair
    )
    f["det_state"] = assign_state(f, cropped, restructure_blind_spot)
    return f
