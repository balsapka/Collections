"""The state tree (states.py, option B) — ONE tree for 60-180 and 180+."""

from __future__ import annotations

from .core import journey_features

STATE_RULES = {
    "epd_max_history": 3,  # [business] months of history before the spell (blip incl.)
    "epd_max_blips": 1,  # [business]
    "straight_max_runup": 3,  # last clean month -> first month at 4
    "stabilized_min_in_band": 5,  # [business] of the last 6 months within today's bucket ±1
    "stabilized_long_run_months": 6,  # [business]
    "stabilized_long_run_max_rise": 1,  # [business]
    "stabilized_max_bucket": 7,  # [business] canonical: CC 7 / RL 6 = 151-180 DPD. Never at 180+.
    "repeat_min_prior_peak": 3,  # [business] earlier spell reached bucket 3 ...
    "repeat_window_months": 12,  # [business] ... and ended <= 12 months before this one
    "seasoned_min_months": 12,  # [business] months on book before the spell
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


# pylint: disable-next=too-many-return-statements,too-many-arguments
def assign_state(
    f: dict,
    cropped: bool,
    restructure_blind_spot: bool = False,
    ecl_gap_blind_spot: bool = False,
) -> str:
    """One state per account, same tree and vocabulary in both segments. First 'yes' wins.

    ECL  a confirmed per-account source gap (RL ECL/DPL union seam, RL-A4-5/RL-A4-6) means
                             we have no reliable signal about this account's shape before
                             the visible window AT ALL, not just its exact onset month ->
                             bypasses the whole cascade: stabilized if Q2, else unknown
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
    # "Genuinely observed from a clean start" covers two distinct blind spots: a Stage-1
    # window crop (floor date / unresolvable gap / dataset edge), OR a restructured account
    # whose own first row is a fresh contract_id, not a fresh delinquency journey — the
    # predecessor contract's history is invisible to this engine either way (R13). A normal
    # (non-restructured) CC account structurally cannot observe its first-ever billing cycle
    # already delinquent (DPD >= 2 requires a prior unpaid cycle to exist first); RL's
    # native-bucket-1 start remains legitimate for a genuinely fresh, non-restructured loan.
    history_blind = cropped or restructure_blind_spot
    # Q2 stabilized — computed up front: both Q0 and the main sequence below consult it.
    stab = f["b_now"] <= p["stabilized_max_bucket"] and (
        f["last6_in_band"] >= p["stabilized_min_in_band"]
        or (
            f["months_since_4"] >= p["stabilized_long_run_months"]
            and f["chg_6m"] <= p["stabilized_long_run_max_rise"]
        )
    )
    # ECL — a confirmed per-account source gap (RL ECL/DPL union seam) means we have no
    # reliable signal about this account's shape before the visible window AT ALL, not
    # just its exact onset month. Unlike cropped/restructure_blind_spot (which still
    # trust the visible run-up's shape for Q3/Q4), this also disqualifies that shape,
    # since the run-up itself may be a window-boundary artifact of the data gap, not the
    # account's true history — bypasses the whole cascade. This is the only path that
    # reaches "unknown" for an EPD-shaped (clean-then-delinquent) sequence, which
    # starts_delinquent-gated Q0 structurally cannot do (RL-A4-7).
    if ecl_gap_blind_spot:
        return "stabilized" if stab else "unknown"
    # Q0 — only a confidence guard when history before the window is genuinely
    # missing (history_blind). When history_blind=False we trust we've seen the
    # whole observed journey, so a delinquent oldest month is not evidence of
    # missing history (e.g. RL native bucket 1 = "1-30 DPD" already counts as
    # delinquent for a loan that missed its very first EMI) — fall through to
    # the normal cascade instead.
    if f["starts_delinquent"] and history_blind:
        return "stabilized" if stab else "unknown"
    # Q1
    if (
        f["months_before_spell"] <= p["epd_max_history"]
        and f["n_blips"] <= p["epd_max_blips"]
        and f["n_prior_episodes"] == 0
        and f["spell_pay_events"] == 0
        and not history_blind
    ):
        return "early_payment_default"
    # Q2
    if stab:
        return "stabilized"
    # Q3
    if f["gap_prior_peak3"] <= p["repeat_window_months"]:
        return "repeat_delinquent"
    # Q4
    if f["runup_len"] <= p["straight_max_runup"]:
        if f["months_before_spell"] >= p["seasoned_min_months"] or history_blind:
            return "straight_roller_seasoned"
        return "straight_roller_early_life"
    # else
    return "slow_roller"


def classify(  # pylint: disable=too-many-positional-arguments
    buckets_native: list[int],
    cropped: bool,
    offset: int,
    canon_top: int,
    repair: bool = True,
    restructure_blind_spot: bool = False,
    ecl_gap_blind_spot: bool = False,
) -> dict:
    """Features + state for one account (native buckets, oldest -> newest)."""
    f = journey_features(
        [max(x + offset, 1) for x in buckets_native], canon_top, repair
    )
    f["det_state"] = assign_state(
        f, cropped, restructure_blind_spot, ecl_gap_blind_spot
    )
    return f
