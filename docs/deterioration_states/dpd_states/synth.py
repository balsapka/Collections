"""Synthetic DPD bucket histories for the bucket 4–7 spine.

Each account gets a full LIFECYCLE: from opening, through the run-up, until it exits
at bucket 8. A snapshot is then taken the way a real one is: an account is in the
spine with probability proportional to the months it spends in buckets 4–7 (so long
holders are over-represented), and its history is cut at a random one of those months.
Because the future is simulated too, monthly roll rates can be measured on the spine
and calibrated to the bank's observed rates (ROLL_TARGET), and 6-month outcomes kept.

Real-data effects layered on top: payment holidays (bucket frozen, nothing paid) and
billing-cycle artefacts (+2 jump next to a fake hold: 3 3 5 or 3 5 5 for 3 4 5).

Strings are emitted with the CURRENT bucket leftmost (bank convention). 0 ≡ 1.
Archetype weights are shares of the INFLOW into bucket 4, not of the spine.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SPINE = (4, 5, 6, 7)
EXIT = 8
ROLL_TARGET = {4: 0.70, 5: 0.80, 6: 0.90, 7: 0.95}   # observed monthly roll rates

P_ONE = 0.05                # chance a normal month shows as bucket 1 instead of 0
P_BLIPPY = 0.30             # share of clean stretches that carry one-month blips to 2
BLIP_RATE = (0.02, 0.10)    # per-month blip probability for a blippy stretch
P_CURE_FROM_4PLUS = 0.05    # full cures to 0 from bucket 4+ are rare
P_HOLIDAY = 0.015           # lifecycles with a payment holiday (bucket frozen 3–6 months)
P_CYCLE_JUMP = 0.01         # per straight-roll triple: reported as 3 3 5 or 3 5 5

# Post-4 monthly roll probability for the "keeps rolling" archetypes. Calibrated by
# calibrate() so that spine-level roll rates match ROLL_TARGET.
Q_ROLL = {4: 0.95, 5: 0.95, 6: 0.95, 7: 0.97}
P_PAY2_POST4 = 0.10         # of non-roll months after 4, share paying 2 months (back 1)


def _merged(x: int) -> int:
    return max(x, 1)


def _tenure(rng, lo: int = 1) -> int:
    """Clean months before the first real spell: one skewed distribution for the whole
    book (median ~4y), so tenure is continuous across patterns — no planted gaps."""
    return int(np.clip(rng.gamma(2.0, 28.0), lo, 180))


def _normal(rng, n: int) -> list[int]:
    """Clean months; some stretches carry one-month blips (0 0 2 0 0)."""
    rate = rng.uniform(*BLIP_RATE) if rng.random() < P_BLIPPY else 0.0
    out = []
    while len(out) < n:
        if rate and len(out) > 0 and out[-1] <= 1 and rng.random() < rate and len(out) < n - 1:
            out += [2, 0]
        else:
            out.append(1 if rng.random() < P_ONE else 0)
    return out[:n]


def _roll_to(path: list[int], target: int) -> None:
    """Straight roll: one bucket per month (paid nothing) until `target`."""
    while _merged(path[-1]) < target:
        path.append(_merged(path[-1]) + 1)


def _post4(path: list[int], rng) -> None:
    """After reaching 4: roll with Q_ROLL, otherwise pay one month (hold) or,
    rarely, two months (back one bucket) — until exit at 8."""
    while path[-1] < EXIT:
        b = path[-1]
        if rng.random() < Q_ROLL.get(b, 1.0):
            path.append(b + 1)
        elif rng.random() < P_PAY2_POST4:
            path.append(b - 1)
        else:
            path.append(b)


def _cure(path: list[int], rng) -> None:
    """Pay back to normal, in one go or in two steps."""
    b = _merged(path[-1])
    if b > 2 and rng.random() < 0.4:
        path.append(b - 1)
    path.append(0)


# --- archetypes: each returns a full lifecycle ending at EXIT ----------------

def bust_out(rng) -> list[int]:
    """0 0 2 3 4 5 or 0 2 0 2 3 4 — at most 3 months of history before rolling in, at most
    one blip (a payoff from 2, never higher) inside it, then gone."""
    if rng.random() < 0.3:
        path = [0, 2, 0]                          # one-shot payoff, only ever from 2
    else:
        path = [0] * int(rng.integers(1, 4))
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def clean_abrupt_shock(rng) -> list[int]:
    """0 0 0 … 0 2 3 4 5 6 7 — clean, then a straight roll. Tenure from the book-wide
    distribution, so some are short and genuinely hard to tell from a bust-out."""
    path = _normal(rng, _tenure(rng, lo=3))
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def slow_slide(rng) -> list[int]:
    """0 0 0 0 2 2 3 3 4 5 6 — monotonic but slower than one bucket a month: pays one
    month's due now and then (stays in the same bucket), at least once on the way to 4.
    Never pays 2+ months, so never goes back. After 4 rolls like the rest."""
    path = _normal(rng, _tenure(rng, lo=6))
    steps = [2, 3]
    must_hold = int(rng.choice(steps))
    for level in steps:
        path.append(level)
        if level == must_hold or rng.random() < 0.3:
            path.append(level)
    path.append(4)
    _post4(path, rng)
    return path


def repeat_episodes(rng) -> list[int]:
    """Earlier episodes cured to normal, e.g. 0 0 2 2 3 3 2 0 2 3 4 5 (gap can be 1 month).
    Tenure can be very short: 0 2 3 4 0 0 2 3 4 5 6 is a repeat, not a bust-out."""
    path = _normal(rng, _tenure(rng, lo=1) if rng.random() < 0.8 else int(rng.integers(1, 6)))
    for _ in range(int(rng.integers(1, 4))):
        peak = 4 if rng.random() < P_CURE_FROM_4PLUS else int(rng.integers(2, 4))
        path.append(2)
        while path[-1] < peak:                    # may hold on the way up
            path += [path[-1]] * int(rng.integers(0, 2)) + [path[-1] + 1]
        path += [path[-1]] * int(rng.integers(0, 3))
        _cure(path, rng)
        path += _normal(rng, int(rng.integers(1, 18)))
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def volatile(rng) -> list[int]:
    """0 0 2 3 2 3 4 2 3 4 5 6 — rolls, pays 2+ months, rolls again, repeatedly (mostly below 4)."""
    path = _normal(rng, _tenure(rng, lo=6))
    path.append(2)
    for _ in range(int(rng.integers(10, 20))):
        b, u = path[-1], rng.random()
        if (u < 0.5 or b == 2) and b < 4:          # oscillates below 4; no stall at 2
            path.append(b + 1)
        elif u < 0.8 and b > 2:
            floor = 1 if (b <= 3 or rng.random() < P_CURE_FROM_4PLUS) else 2
            path.append(max(b - int(rng.integers(1, 3)), floor))
        elif b == 4:
            break
        else:
            path.append(b)
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def dip_and_roll(rng) -> list[int]:
    """0 0 2 3 4 3 4 5 6 — rolls, pays two months once (back one bucket), keeps rolling."""
    path = _normal(rng, _tenure(rng, lo=6))
    peak = int(rng.integers(3, 5))
    _roll_to(path, peak)
    path.append(peak - 1)
    if rng.random() < 0.3:
        path.append(peak - 1)
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def staircase(rng) -> list[int]:
    """0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4 5 — holds several months per level, then steps up."""
    path = _normal(rng, _tenure(rng, lo=6))
    for level in range(2, EXIT):
        path += [level] * (int(rng.integers(2, 8)) if level <= 5 else int(rng.integers(1, 3)))
    path.append(EXIT)
    return path


def stabilized(rng) -> list[int]:
    """0 0 … 2 3 4 5 5 5 4 5 5 5 6 5 5 … — reaches a level and keeps paying around one
    month's due for a long time (±1 bucket), eventually breaks and rolls out."""
    path = _normal(rng, _tenure(rng, lo=6))
    _roll_to(path, int(rng.choice([4, 5, 6], p=[0.6, 0.3, 0.1])))
    for _ in range(int(rng.integers(6, 36))):
        b, u = path[-1], rng.random()
        if u < 0.75:
            path.append(b)
        elif u < 0.87 and b < 6:
            path.append(b + 1)
        elif b > 3:
            path.append(b - 1)
        else:
            path.append(b)
    _roll_to(path, 4)
    _post4(path, rng)
    return path


# Inflow weights tuned so the spine shows bust-out ~6% and stabilized ~6% (the bank's
# actual shares under its own rules) while roll rates still hit ROLL_TARGET.
ARCHETYPES = {                      # name: (share of INFLOW into bucket 4, generator)
    "bust_out": (0.055, bust_out),
    "stabilized": (0.008, stabilized),
    "clean_abrupt_shock": (0.42, clean_abrupt_shock),
    "slow_slide": (0.08, slow_slide),
    "staircase": (0.008, staircase),
    "repeat_episodes": (0.16, repeat_episodes),
    "dip_and_roll": (0.10, dip_and_roll),
    "volatile": (0.10, volatile),
}


# --- real-data effects ---------------------------------------------------------

def _payment_holiday(path: list[int], rng) -> bool:
    """Freeze the bucket for 3–6 months somewhere in the delinquent stretch (nothing paid,
    but it reads exactly like a hold)."""
    idx = [k for k, x in enumerate(path) if 2 <= x < EXIT]
    if not idx or rng.random() >= P_HOLIDAY:
        return False
    k = int(rng.choice(idx))
    path[k + 1:k + 1] = [path[k]] * int(rng.integers(3, 7))
    return True


def _cycle_jumps(path: list[int], rng) -> None:
    """Billing-cycle artefact on straight rolls: true 3 4 5 reported as 3 3 5 or 3 5 5."""
    for k in range(len(path) - 2):
        a, m, z = path[k], path[k + 1], path[k + 2]
        if a >= 2 and m == a + 1 and z == a + 2 and z <= 7 and rng.random() < P_CYCLE_JUMP:
            path[k + 1] = a if rng.random() < 0.5 else a + 2


def _snapshot_rows(n: int, rng, k_future: int = 6) -> list[dict]:
    names = list(ARCHETYPES)
    w = np.array([ARCHETYPES[k][0] for k in names])
    pool_names = rng.choice(names, size=4 * n, p=w / w.sum())
    pool, holiday = [], []
    for k in pool_names:
        p = ARCHETYPES[k][1](rng)
        holiday.append(_payment_holiday(p, rng))
        _cycle_jumps(p, rng)
        pool.append(p)
    months = np.array([sum(1 for x in p if x in SPINE) for p in pool], dtype=float)
    chosen = rng.choice(len(pool), size=n, replace=False, p=months / months.sum())
    rows = []
    for i, j in enumerate(chosen):
        path = pool[j]
        first4 = next(k for k, x in enumerate(path) if x >= 4)
        t = int(rng.choice([k for k, x in enumerate(path) if x in SPINE]))
        fut = path[t + 1:t + 7]
        ext = path[:t + k_future + 1]
        while len(ext) < t + k_future + 1:          # after exit the bucket keeps climbing
            ext.append(min(ext[-1] + 1, 9))
        exit_at = next((k for k, x in enumerate(fut) if x >= EXIT), None)
        rows.append({
            "account_id": f"A{i:06d}",
            "dpd_string": "".join(str(x) for x in reversed(path[:t + 1])),
            "true_archetype": pool_names[j],
            "had_holiday": holiday[j],
            # future — validation only, never used to assign states
            "next_bucket": path[t + 1],
            "next_string": "".join(str(x) for x in reversed(path[:t + 2])),
            "exit_6m": exit_at is not None,
            "bucket_6m": EXIT if exit_at is not None else fut[-1],
            "paid_after_4_so_far": bool((np.diff(path[first4:t + 1]) < 1).any()),
            "latest_string": "".join(str(x) for x in reversed(ext)),   # k_future months later
        })
    return rows


def generate(n: int = 20_000, seed: int = 7) -> pd.DataFrame:
    return pd.DataFrame(_snapshot_rows(n, np.random.default_rng(seed)))


def latest_month_strings(n: int = 20_000, k: int = 6, seed: int = 7) -> pd.DataFrame:
    """What the workplace table looks like for a backtest: accounts that were in the spine
    k months ago, with their DPD string as of the LATEST month (k newer digits on the left;
    after exit the bucket keeps climbing 8, 9, 9 …). Used to test analysis.py end to end."""
    df = pd.DataFrame(_snapshot_rows(n, np.random.default_rng(seed), k_future=k))
    return df[["latest_string", "true_archetype"]].rename(columns={"latest_string": "dpd_string"})


def roll_rates(df: pd.DataFrame) -> pd.Series:
    cur = df.dpd_string.str[0].astype(int)
    return (df.next_bucket >= cur + 1).groupby(cur).mean()


def calibrate(n: int = 10_000, iters: int = 8, seed: int = 11) -> pd.DataFrame:
    """Tune Q_ROLL so spine roll rates match ROLL_TARGET. Returns the iteration log."""
    log = []
    for it in range(iters):
        rr = roll_rates(generate(n, seed + it))
        log.append({"iter": it, **{f"rr_{b}": rr[b] for b in SPINE},
                    **{f"q_{b}": Q_ROLL[b] for b in SPINE}})
        for b in SPINE:
            Q_ROLL[b] = float(np.clip(Q_ROLL[b] + 1.2 * (ROLL_TARGET[b] - rr[b]), 0.3, 0.999))
    return pd.DataFrame(log)
