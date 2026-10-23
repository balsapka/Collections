"""Per-account core — plain Python, no Spark / numpy / pandas (runs inside the UDFs).
Lists run OLDEST -> NEWEST on the canonical scale. Port of the numpy reference
(docs/deterioration_states/dpd_states: features.py). Variable names here deliberately
mirror the reference's own names for line-by-line auditability — do not rename them.
"""

from __future__ import annotations

N, R, H, P = 0, 1, 2, 3
NO_PRIOR = 9999


def _glitches(b: list[int]) -> tuple[list[int], int]:
    """Impossible single-month glitches (4 0 4 -> 4 4 4; 0 3 0 -> 0 1 0). Sequential: a fixed
    month is seen by the next comparison, as in features.py::_glitches."""
    b = list(b)
    n = 0
    for t in range(1, len(b) - 1):
        if b[t] <= 1 and b[t - 1] >= 3 and b[t + 1] >= 3:
            b[t] = b[t - 1]
            n += 1
        elif b[t] >= 3 and b[t - 1] <= 1 and b[t + 1] <= 1:
            b[t] = 1
            n += 1
    return b, n


def _repair(b: list[int]) -> tuple[list[int], int, int]:
    """Undo +2 billing-cycle jumps next to a hold at >=2 (3 3 5 / 3 5 5 -> 3 4 5)."""
    b = list(b)
    repaired = 0
    for i in range(len(b) - 1):
        if b[i + 1] - b[i] != 2:
            continue
        if i >= 1 and b[i] == b[i - 1] and b[i] >= 2:
            b[i] += 1
            repaired += 1
        elif i + 2 < len(b) and b[i + 2] == b[i + 1] and b[i + 1] != 4:
            b[i + 1] -= 1
            repaired += 1
    left = sum(1 for i in range(len(b) - 1) if b[i + 1] - b[i] >= 2)
    return b, repaired, left


def encode(
    b_canon: list[int], repair: bool = True
) -> tuple[list[int], list[int], list[int]]:
    """(b, d, c): repaired buckets, month-on-month change, transition code N/R/H/P.
    repair=False skips _repair() (RL: +2 jumps are real DPD moves, not a billing
    artifact — see constants.py::BucketScheme.repair_jumps)."""
    g = _glitches([max(x, 1) for x in b_canon])[0]
    b = _repair(g)[0] if repair else g
    d = [b[t + 1] - b[t] for t in range(len(b) - 1)]
    c = []
    for t, x in enumerate(d):
        cur = b[t + 1]
        if x == 0:
            c.append(N if cur == 1 else H)
        elif x < 0:
            c.append(P)
        else:
            c.append(R)  # +1 and any leftover +2 read as a roll
    return b, d, c


def _runs(mask: list[bool]) -> list[tuple[int, int]]:
    """(start, end_exclusive) of True runs."""
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = i
        elif not m and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(mask)))
    return out


def _mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


# pylint: disable-next=too-many-locals
def journey_features(
    b_canon: list[int], canon_top: int = 9, repair: bool = True
) -> dict:
    """features.py::journey_features on a canonical bucket list (oldest -> newest).
    canon_top: the ceiling bucket (CC 9, RL 7 -> 8). A hold AT the ceiling is not a payment
    (the bucket cannot rise), so it is not counted in spell_pay_events.
    repair=False (RL): skip the +2 billing-cycle-jump fixer entirely — n_jumps_repaired
    is 0 and n_jumps_left is counted on the glitch-fixed but unrepaired array."""
    raw = [max(x, 1) for x in b_canon]
    g, n_glitches = _glitches(raw)
    if repair:
        _, n_repaired, n_jumps_left = _repair(g)
    else:
        n_repaired = 0
        n_jumps_left = sum(1 for i in range(len(g) - 1) if g[i + 1] - g[i] >= 2)
    b, d, c = encode(b_canon, repair)
    if b[-1] < 2:
        raise ValueError("not in a delinquent spell (current bucket < 2)")
    paid = [max(1 - x, 0) for x in d]

    # episodes: every maximal run at or above delinquency; the last one is "the current
    # spell", everything before it is prior history to classify as blip vs. real episode.
    episodes = _runs([x >= 2 for x in b])
    sp_start, sp_end = episodes[-1]
    is_blip = [e - s <= 2 and max(b[s:e]) <= 2 for s, e in episodes[:-1]]
    prior = [ep for ep, blip in zip(episodes[:-1], is_blip) if not blip]
    first_spell = (prior + [episodes[-1]])[0][0]

    def gap_prior(peak: int) -> int:
        ends = [e for s, e in prior if max(b[s:e]) >= peak]
        return sp_start - ends[-1] if ends else NO_PRIOR

    # t0: one month before the current spell starts (clamped at 0) — the transition code
    # at t0 is the move INTO the spell, so the spell's own transition window starts there.
    t0 = max(sp_start - 1, 0)
    sp_c = c[t0 : sp_end - 1]
    hold_runs = [e - s for s, e in _runs([x == H for x in sp_c])]
    first4 = sp_start + next((i for i, x in enumerate(b[sp_start:sp_end]) if x >= 4), 0)
    ru_c = c[t0:first4]
    months_since_4 = len(b) - 1 - first4
    # w0/w_c: the recent window (last 6 transitions, but never reaching before t0) used
    # for the "is this account still rolling/paying lately" features.
    w0 = max(len(c) - 6, t0)
    w_c = c[w0:]
    # tail_hold: months held (unchanged, not clean) at the very end of the history.
    tail_hold = 0
    for x in reversed(c):
        if x != H:
            break
        tail_hold += 1
    b_now = b[-1]
    return {
        "b_now": b_now,
        "hist_len": len(b),
        "months_before_spell": sp_start,
        "clean_tenure_first": first_spell,
        "n_blips": sum(is_blip),
        "n_prior_episodes": len(prior),
        "max_prior_bucket": max((max(b[s:e]) for s, e in prior), default=0),
        "clean_gap_before_current": sp_start - (prior[-1][1] if prior else 0),
        "gap_prior_peak2": gap_prior(2),
        "gap_prior_peak3": gap_prior(3),
        "gap_prior_peak4": gap_prior(4),
        "runup_len": first4 - sp_start + 1,
        "runup_holds": sum(1 for x in ru_c if x == H),
        "runup_pays": sum(1 for x in ru_c if x == P),
        "spell_len": sp_end - sp_start,
        "spell_pay_events": sum(
            1
            for t in range(t0, sp_end - 1)
            if c[t] != R and not (c[t] == H and b[t + 1] >= canon_top)
        ),
        "max_hold_run": max(hold_runs, default=0),
        "months_since_4": months_since_4,
        "post4_paid_rate": _mean(paid[first4:]) if months_since_4 > 0 else 0.0,
        "rec_roll_rate": _mean(x == R for x in w_c) if w_c else 1.0,
        "rec_paid_rate": _mean(paid[w0:]) if w_c else 0.0,
        "paid_any_3m": any(x > 0 for x in paid[-3:]),
        "current_hold_run": tail_hold,
        "last6_in_band": sum(1 for x in b[-6:] if abs(x - b_now) <= 1),
        "chg_6m": b_now - b[max(len(b) - 7, 0)],
        "left_censored": sp_start == 0,
        "starts_delinquent": b[0] >= 2,
        "n_glitches": n_glitches,
        "n_jumps_repaired": n_repaired,
        "n_jumps_left": n_jumps_left,
    }
