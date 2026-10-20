"""Unit tests for crx_persona/_dpd_journey.py — self-contained (no Spark session, no data).

Workplace location: src/tests/nodes/crx_persona/test_dpd_journey.py.
Run: python -m pytest src/tests/nodes/crx_persona

The cases are the business edge cases agreed for the deterioration states (option B),
the history-window (crop) cases, the ceiling / unknown rules, and the Stage 1 gap rules.
Exact parity of the engine with the numpy reference was proven separately
(docs/deterioration_states/spark/tests/test_parity.py, recoverable from BUNDLE.md).
"""
from __future__ import annotations

import pytest

from enbd_collections.pipelines.crx_persona import _dpd_journey as J

# (oldest -> newest CC buckets, expected option-B state, why)
CASES = [   ('0 2 0 2 3 4', 'early_payment_default', '3 months incl. one blip, then straight roll'),
    ('0 0 0 2 3 4', 'early_payment_default', '3 clean months, straight roll'),
    ('0 2 3 4 5', 'early_payment_default', '1 clean month'),
    ('0 0 2 0 2 3 4', 'straight_roller_early_life', '4 months of history: too long for EPD'),
    (   '0 0 0 0 0 0 2 3 4',
        'straight_roller_early_life',
        '6 clean months: early-life default, not EPD'),
    ('0 2 0 2 0 2 3 4', 'straight_roller_early_life', 'two blips: not EPD'),
    ('0 2 3 4 0 0 2 3 4 5 6', 'repeat_delinquent', 'paid off from 4, then relapsed'),
    ('0 0 2 2 3 4', 'slow_roller', 'held once on the way down'),
    ('0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4 5', 'stabilized', 'staircase holding at 4 then one step'),
    ('000000000000002345', 'straight_roller_seasoned', '14 clean months, straight roll'),
    (   '0000000000000234444567',
        'straight_roller_seasoned',
        'held at 4, then rolled 3 buckets: not stable'),
    ('0000000000000023455555', 'stabilized', 'holding at 5'),
    ('00000000234443345433456554', 'stabilized', 'oscillating payer (example 1)'),
    (   '00000000234443345433456654',
        'stabilized',
        'oscillating payer that just paid down 6-5-4 (example 2)'),
    (   '0 0 2 3 4 4 4 4 4 4',
        'stabilized',
        'entered like EPD but pays the monthly due since: not EPD'),
    (   '0 0 2 3 4 4 5 6',
        'straight_roller_early_life',
        'entered like EPD, paid once at 4: EPD needs no payment'),
    ('4 5 6 7', 'unknown', 'string starts delinquent (restructured / missing history)'),
    ('4 4 4 4 4 5', 'stabilized', 'starts delinquent but holding: stabilized needs only 6 months'),
    ('0 0 0 2 3 4 4 4 4 4', 'stabilized', 'journey observed from 0 DPD, holding at 4'),
    (   '0000000000000000224',
        'straight_roller_seasoned',
        '+2 jump after a hold at 2: repaired to 2 3 4'),
    (   '00000000000000002244',
        'straight_roller_seasoned',
        'same account a month later: fixed state must not change'),
    ('000034', 'straight_roller_early_life', 'jump from clean to 3: no clean month is borrowed'),
    (   '0 2 3 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 3 4',
        'straight_roller_seasoned',
        'cured 20 months earlier: outside 12-month window'),
    (   '0 2 3 4 0 0 0 0 0 0 0 0 2 3 4 5',
        'repeat_delinquent',
        'cured 8 months earlier: repeat delinquent'),
    (   '0000000000000000 2 3 4 4 0 4 5',
        'stabilized',
        'single 0 inside a spell at 4 is a glitch, not a cure'),
    (   '0000 3 0000000000000 2 3 4',
        'straight_roller_seasoned',
        'single spike 0 3 0 is a glitch, not an earlier spell')]

# (oldest -> newest, months kept by the history window, expected option-B state, why)
CROP_CASES = [   (   '00000000002344545454545454545454545454545454545454',
        32,
        'stabilized',
        'spell older than the window: not a data-quality case; long-run holder -> stabilized'),
    (   '0000000000000000000000000000000000000000234',
        32,
        'straight_roller_seasoned',
        'long clean history cropped: still seasoned'),
    (   '0000000000234',
        6,
        'straight_roller_seasoned',
        'cropped to 0 0 0 2 3 4: looks like EPD, but older than the window'),
    ('0 0 0 2 3 4', 32, 'early_payment_default', 'short history, not cropped: EPD')]

# 180+ segment (canonical cap: CC 9, RL 7 -> 8) and the ceiling / unknown rules
CASES_180 = [
    ("cc", [0] * 20 + [2, 3, 4, 5, 6, 7, 8, 9] + [9] * 12, "straight_roller_seasoned"),  # at the cap: not stabilized
    ("cc", [0] * 20 + [2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8], "stabilized"),               # holding at 8, below the cap
    ("cc", [8, 9, 9, 9, 9, 9, 9], "unknown"),                                            # journey start not observed
    ("cc", [0] * 20 + [2, 3, 4, 5, 6, 7, 8, 9, 9, 8, 9], "paying_in_default"),
    ("rl", [0] * 20 + [1, 2, 3, 4, 5, 6, 7, 7, 7], "straight_roller_seasoned"),
    ("rl", [0] * 20 + [1, 2, 3, 4, 5, 6, 7, 7, 6, 7], "paying_in_default"),
    ("rl", [7, 7, 7, 7], "unknown"),
    ("rl", [0, 0, 1, 2, 3, 4, 5, 6, 7], "early_payment_default"),
    ("rl", [0] * 20 + [1, 2, 3, 4, 5] + [6] * 12 + [7, 7], "broken_payer"),
    ("rl", [0] * 20 + [1, 2, 3, 4, 5, 6, 7] + [7] * 12, "straight_roller_seasoned"),     # 12 months at the cap
]
SCHEME = {"cc": (0, 9), "rl": (1, 8)}     # (offset, canonical cap)


def _to_rl(cc: list[int]) -> list[int]:
    """CC buckets -> RL native (CC 0/1 -> 0, CC 2 -> 1, ..., CC 8/9 -> 7)."""
    return [min(max(x, 1), 8) - 1 for x in cc]


def _chron(text: str) -> list[int]:
    return [int(ch) for ch in text.replace(" ", "")]


@pytest.mark.parametrize("chron,want,why", CASES)
@pytest.mark.parametrize("product", ["cc", "rl"])
def test_business_case(product, chron, want, why):
    b = _chron(chron)
    buckets = b if product == "cc" else _to_rl(b)
    off, top = SCHEME[product]
    assert J.classify(buckets, False, off, top, "60_180", "B_balanced_6")["det_state"] == want, why


@pytest.mark.parametrize("chron,n,want,why", CROP_CASES)
def test_crop_case(chron, n, want, why):
    b = _chron(chron)
    got = J.classify(b[-n:], len(b) >= n, 0, 9, "60_180", "B_balanced_6")["det_state"]
    assert got == want, why


@pytest.mark.parametrize("product,buckets,want", CASES_180)
def test_180_and_ceiling(product, buckets, want):
    off, top = SCHEME[product]
    assert J.classify(buckets, False, off, top, "180_plus", "B_balanced_6")["det_state"] == want


def test_every_option_is_mece():
    """Each option returns exactly one known state for every case."""
    for option in J.OPTIONS:
        for chron, _, _ in CASES:
            assert J.classify(_chron(chron), False, 0, 9, "60_180", option)["det_state"] in J.DISPLAY_NAMES


def _hist(rows, first_raw=None, gmin=0, offset=0, fill=True, how="truncate", max_inf=2):
    first_raw = first_raw if first_raw is not None else min(r[0] for r in rows)
    return J.build_history(rows, first_raw, gmin, offset, fill, how, True, max_inf)


@pytest.mark.parametrize("kwargs,check", [
    (dict(rows=[(100, 1, 3), (101, 5, 4), (101, 9, 5), (102, 1, 5)]),
     lambda r: r["buckets"] == [3, 5, 5] and r["n_dup_month_rows"] == 1),            # latest in month wins
    (dict(rows=[(100, 1, 3), (101, 5, 4), (101, 5, 6), (102, 1, 6)]),
     lambda r: r["buckets"] == [3, 6, 6]),                                           # same day: worst wins
    (dict(rows=[(100, 1, 4), (102, 1, 4)]),
     lambda r: r["buckets"] == [4, 4, 4] and r["n_gap_months_filled"] == 1),         # hold through
    (dict(rows=[(100, 1, 0), (102, 1, 1)]),
     lambda r: r["buckets"] == [0, 0, 1] and r["n_months_truncated"] == 0),          # CC 0 _ 1 is clean
    (dict(rows=[(100, 1, 3), (103, 1, 6)]),
     lambda r: r["buckets"] == [3, 4, 5, 6] and r["n_gap_months_rolled"] == 2),      # straight roll
    (dict(rows=[(100, 1, 0), (102, 1, 2)], offset=1),
     lambda r: r["buckets"] == [0, 1, 2]),                                           # RL straight roll
    (dict(rows=[(100, 1, 0), (101, 1, 0), (105, 1, 4), (106, 1, 5)]),
     lambda r: r["buckets"] == [4, 5] and r["n_months_truncated"] == 5
     and r["history_cropped"] and r["legacy_drop"]),                                 # unresolvable: truncate
    (dict(rows=[(100, 1, 3), (102, 1, 4)]),
     lambda r: r["buckets"] == [3, 3, 4] and r["n_gap_months_inferred"] == 1),       # inferred, roll late
    (dict(rows=[(100, 1, 6), (103, 1, 3)]),
     lambda r: r["buckets"] == [6, 6, 6, 3] and r["n_gap_months_inferred"] == 2),    # carry, pay at end
    (dict(rows=[(100, 1, 3), (102, 1, 4)], max_inf=0),
     lambda r: r["buckets"] == [4] and r["n_months_truncated"] == 2),                # inference off
    (dict(rows=[(100, 30, 2), (101, 60, 3), (101, 61, 4), (103, 90, 5)]),
     lambda r: r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1),      # cycle shift forward
    (dict(rows=[(100, 1, 2), (102, 50, 3), (102, 80, 4), (103, 90, 5)]),
     lambda r: r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1),      # cycle shift back
    (dict(rows=[(100, 1, 0), (102, 1, 4)], how="drop", max_inf=0),
     lambda r: r["build_status"] == "dropped_unresolvable_gap"),
    (dict(rows=[(100, 1, 0), (101, 1, 2)], fill=False),
     lambda r: r["history_cropped"] is False),
    (dict(rows=[(110, 1, 0), (111, 1, 2)], first_raw=90),
     lambda r: r["history_cropped"]),                                                # older rows before the floor
    (dict(rows=[(110, 1, 0), (111, 1, 2)], gmin=110),
     lambda r: r["history_cropped"]),                                                # starts with the source
])
def test_build_history(kwargs, check):
    assert check(_hist(**kwargs))


def test_build_history_empty():
    assert J.build_history([], 100, 0, 0)["build_status"] == "no_rows_in_window"
