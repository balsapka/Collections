"""Encode DPD strings and derive per-account journey features.

Encoding (time runs oldest -> newest after reversing the string):
    b : bucket per month, 0 merged into 1
    d : month-on-month difference. Months paid that month = 1 - d:
        +1 roll (paid nothing) / 0 hold (paid one month's due) / -k (paid k+1 months)
    c : state code per transition
        0 = N  normal (stayed at <=1)
        1 = R  roll, paid nothing (d = +1)
        2 = H  hold at >=2, paid one month (d = 0)
        3 = P  moved back, paid 2+ months (d < 0); back to <=1 is a cure

Data artefacts are cleaned before encoding (all counted, never silent):
  * impossible one-month glitches — a single month at 0/1 between two months at 3+ (a cure
    cannot be followed by a jump to 3+), or a single month at 3+ between two clean months
    (an account cannot jump from 0 to 3) — are read as a hold and as a clean month;
  * billing-cycle +2 jumps (3 3 5 or 3 5 5 for a true 3 4 5) are rewritten as the straight
    roll. The hold BEFORE the jump is preferred as the artefact (it is already observed), the
    hold after only if that does not move a month observed at 4 back below 4; a hold at 0/1
    is never treated as an artefact. Any other +2 stays and is read as a roll.

Features are built to be invariant to the current bucket, which for most of the spine is
only a clock (months since reaching 4): lifetime and run-up features are fixed once the
account passes 4. The two exceptions are deliberate current-behaviour inputs to the
'stabilized' question: last6_in_band, and months_since_4 + chg_6m (long-run clause).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N, R, H, P = 0, 1, 2, 3
LETTERS = "NRHP"
NO_PRIOR = 9999          # gap value when there is no qualifying earlier spell


def _glitches(b: np.ndarray) -> tuple[np.ndarray, int]:
    """Impossible single-month glitches. Returns (b, n_fixed)."""
    b = b.copy()
    n = 0
    for t in range(1, len(b) - 1):
        if b[t] <= 1 and b[t - 1] >= 3 and b[t + 1] >= 3:      # 4 0 4 -> 4 4 4
            b[t] = b[t - 1]
            n += 1
        elif b[t] >= 3 and b[t - 1] <= 1 and b[t + 1] <= 1:    # 0 3 0 -> 0 0 0
            b[t] = 1
            n += 1
    return b, n


def _repair(b: np.ndarray) -> tuple[np.ndarray, int, int]:
    """Undo +2 billing-cycle jumps next to a hold at >=2. Returns (b, repaired, left)."""
    b = b.copy()
    repaired = 0
    for i in range(len(b) - 1):
        if b[i + 1] - b[i] != 2:
            continue
        if i >= 1 and b[i] == b[i - 1] and b[i] >= 2:                     # 3 3 5 -> 3 4 5
            b[i] += 1
            repaired += 1
        elif i + 2 < len(b) and b[i + 2] == b[i + 1] and b[i + 1] != 4:    # 3 5 5 -> 3 4 5
            b[i + 1] -= 1
            repaired += 1
    left = int((np.diff(b) >= 2).sum())
    return b, repaired, left


def _digits(dpd: str) -> np.ndarray:
    if not isinstance(dpd, str) or not dpd.isdigit():
        raise ValueError(f"DPD string must be digits only, got {dpd!r}")
    return np.maximum(np.array([int(ch) for ch in reversed(dpd)]), 1)


def encode(dpd: str, repair: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    b = _digits(dpd)
    if repair:
        b = _repair(_glitches(b)[0])[0]
    d = np.diff(b)
    cur = b[1:]
    c = np.full(len(d), R)                  # +1 and any leftover +2 read as a roll
    c[(d == 0) & (cur == 1)] = N
    c[(d == 0) & (cur >= 2)] = H
    c[d < 0] = P
    return b, d, c


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """(start, end_exclusive) of True runs."""
    edges = np.diff(np.concatenate([[0], mask.astype(int), [0]]))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def journey_features(dpd: str) -> dict:
    g, n_glitches = _glitches(_digits(dpd))
    _, n_repaired, n_jumps_left = _repair(g)
    b, d, c = encode(dpd)
    if b[-1] < 2:
        raise ValueError(f"not in a delinquent spell (current bucket < 2): {dpd!r} — "
                         "apply the spine filter (current bucket 4–7) before build_features")
    paid = np.clip(1 - d, 0, None)                      # months paid per month

    episodes = _runs(b >= 2)                            # current spell is the last one
    sp_start, sp_end = episodes[-1]
    # a blip is a 1–2 month excursion that never went past 2 (0 0 2 0 0)
    is_blip = [e - s <= 2 and b[s:e].max() <= 2 for s, e in episodes[:-1]]
    prior = [ep for ep, blip in zip(episodes[:-1], is_blip) if not blip]
    first_spell = (prior + [episodes[-1]])[0][0]        # blips don't end clean tenure

    def gap_prior(peak: int) -> int:
        """Clean months between the end of the most recent earlier (non-blip) spell that
        reached `peak` and the start of the current spell. Fixed once the spell starts."""
        ends = [e for s, e in prior if b[s:e].max() >= peak]
        return int(sp_start - ends[-1]) if ends else NO_PRIOR

    # transitions landing inside the current spell
    t0 = max(sp_start - 1, 0)
    sp_c, sp_d = c[t0:sp_end - 1], d[t0:sp_end - 1]
    hold_runs = [e - s for s, e in _runs(sp_c == H)]

    # run-up: last clean month -> first month at 4+. Fixed once they pass 4.
    first4 = sp_start + int(np.argmax(b[sp_start:sp_end] >= 4))
    ru_c = c[t0:first4]
    months_since_4 = len(b) - 1 - first4

    # recent behaviour: last 6 months, but only inside the current spell
    w0 = max(len(c) - 6, t0)
    w_c = c[w0:]
    tail_hold = 0
    for x in c[::-1]:
        if x != H:
            break
        tail_hold += 1

    b_now = int(b[-1])
    return {
        "b_now": b_now,
        "hist_len": len(b),
        # lifetime
        "months_before_spell": int(sp_start),
        "clean_tenure_first": int(first_spell),
        "n_blips": int(sum(is_blip)),
        "n_prior_episodes": len(prior),
        "max_prior_bucket": int(max((b[s:e].max() for s, e in prior), default=0)),
        "clean_gap_before_current": int(sp_start - (prior[-1][1] if prior else 0)),
        "gap_prior_peak2": gap_prior(2),
        "gap_prior_peak3": gap_prior(3),
        "gap_prior_peak4": gap_prior(4),
        # run-up (fixed once past 4)
        "runup_len": int(first4 - sp_start + 1),        # 3 = straight 2-3-4
        "runup_holds": int((ru_c == H).sum()),
        "runup_pays": int((ru_c == P).sum()),
        # current spell
        "spell_len": int(sp_end - sp_start),
        "spell_pay_events": int((sp_c != R).sum()),     # months in this spell with a payment
        "max_hold_run": int(max(hold_runs, default=0)),
        "months_since_4": int(months_since_4),          # months since first reaching 4 this spell
        "post4_paid_rate": float(paid[first4:].mean()) if months_since_4 > 0 else 0.0,
        # recent behaviour (rates within the current spell, last 6 months)
        "rec_roll_rate": float((w_c == R).mean()) if len(w_c) else 1.0,
        "rec_paid_rate": float(paid[w0:].mean()) if len(w_c) else 0.0,
        "paid_any_3m": bool((paid[-3:] > 0).any()),     # DPD proxy of 'money coming in'
        "current_hold_run": tail_hold,
        "last6_in_band": int((np.abs(b[-6:] - b_now) <= 1).sum()),
        "chg_6m": int(b_now - b[max(len(b) - 7, 0)]),
        # data quality
        "left_censored": bool(sp_start == 0),           # history starts inside the spell
        "starts_delinquent": bool(b[0] >= 2),           # oldest observed month already delinquent
        "n_glitches": n_glitches,
        "n_jumps_repaired": n_repaired,
        "n_jumps_left": n_jumps_left,
    }


def build_features(df: pd.DataFrame, col: str = "dpd_string") -> pd.DataFrame:
    if len(df) == 0:
        raise ValueError("build_features got an empty frame — check the spine filter / sample")
    feats = pd.DataFrame([journey_features(s) for s in df[col]], index=df.index)
    return pd.concat([df, feats], axis=1)
