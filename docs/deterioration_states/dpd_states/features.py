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

Billing-cycle artefacts are repaired before encoding: a +2 jump next to a hold
(3 3 5 or 3 5 5) is rewritten as the straight roll it was (3 4 5). A +2 jump with no
neighbouring hold stays and is read as a roll (paid nothing); both are counted.

Features are built to be invariant to the current bucket, which for most of the
spine is only a clock (months since reaching 4): lifetime and run-up features are
fixed once the account passes 4, and recent-behaviour features are rates within the
current spell.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N, R, H, P = 0, 1, 2, 3
LETTERS = "NRHP"


def _repair(b: np.ndarray) -> tuple[np.ndarray, int, int]:
    """Undo +2 billing-cycle jumps that sit next to a hold. Returns (b, repaired, left)."""
    b = b.copy()
    repaired = 0
    for i in np.flatnonzero(np.diff(b) == 2):
        if i + 2 < len(b) and b[i + 2] == b[i + 1]:          # 3 5 5 -> 3 4 5
            b[i + 1] -= 1
            repaired += 1
        elif i >= 1 and b[i] == b[i - 1]:                     # 3 3 5 -> 3 4 5
            b[i] += 1
            repaired += 1
    left = int((np.diff(b) >= 2).sum())
    return b, repaired, left


def encode(dpd: str, repair: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    b = np.maximum(np.array([int(ch) for ch in reversed(dpd)]), 1)
    if repair:
        b = _repair(b)[0]
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
    raw = np.maximum(np.array([int(ch) for ch in reversed(dpd)]), 1)
    _, n_repaired, n_jumps_left = _repair(raw)
    b, d, c = encode(dpd)
    paid = np.clip(1 - d, 0, None)                      # months paid per month

    episodes = _runs(b >= 2)                            # current spell is the last one
    sp_start, sp_end = episodes[-1]
    # a blip is a 1–2 month excursion that never went past 2 (0 0 2 0 0)
    is_blip = [e - s <= 2 and b[s:e].max() <= 2 for s, e in episodes[:-1]]
    prior = [ep for ep, blip in zip(episodes[:-1], is_blip) if not blip]
    first_spell = (prior + [episodes[-1]])[0][0]        # blips don't end clean tenure

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
        # run-up (fixed once past 4)
        "runup_len": int(first4 - sp_start + 1),        # 3 = straight 2-3-4
        "runup_holds": int((ru_c == H).sum()),
        "runup_pays": int((ru_c == P).sum()),
        # current spell
        "spell_len": int(sp_end - sp_start),
        "max_hold_run": int(max(hold_runs, default=0)),
        "months_since_4": int(months_since_4),          # months in buckets 4+ this spell
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
        "n_jumps_repaired": n_repaired,
        "n_jumps_left": n_jumps_left,
    }


def build_features(df: pd.DataFrame, col: str = "dpd_string") -> pd.DataFrame:
    feats = pd.DataFrame([journey_features(s) for s in df[col]], index=df.index)
    return pd.concat([df, feats], axis=1)
