"""DPD-journey deterioration states — one engine for credit cards (CC) and retail loans (RL).

Replaces the window-function port (resolve_gaps / encode_transitions / classify_from_grid).
Spark does what Spark is good at — scoping, the history floor, and ONE shuffle that gathers
each account's monthly buckets into an array. The journey logic then runs per account as a
plain-Python port of the signed-off numpy reference (docs/deterioration_states/dpd_states:
features.py, states.py option B). Sequential rules (glitch fix, +2 jump repair, runs
of months) are loops, exactly as in the reference — no lag/lead approximation, no cascade
divergence. Parity with the reference is a test (tests/test_parity.py), not a hope.

Bucket numbering
----------------
Every rule is written once, on the CC scale ("canonical"):
    CC  0 = no due, 1 = current, 2 = 1-30 DPD, 3 = 31-60, 4 = 61-90 ... 7 = 151-180,
        8 = 181-210, 9 = 210+ (cap)
    RL  0 = 0 DPD,  1 = 1-30 DPD, 2 = 31-60 ... 6 = 151-180, 7 = 180+ (cap)
canonical = max(native + offset, 1): CC offset 0, RL offset 1 (0 and 1 are both "clean").
So the 60-180 DPD spine is canonical 4-7 for both (CC native 4-7, RL native 3-6), and the
180+ segment is canonical 8+ (CC native 8-9, RL native 7). Outputs carry NATIVE buckets.

One state tree and one vocabulary for both segments (7 states): unknown, early_payment_default,
stabilized, repeat_delinquent, straight_roller_seasoned, straight_roller_early_life,
slow_roller. Stabilized only up to 151-180 DPD (never at 180+); holds at the ceiling bucket
are not payments. The segment only decides which accounts are classified.

Two stages (two Kedro nodes per product)
----------------------------------------
build_dpd_sequences   (account_id, obs_date, dlq_bucket) long history
                      -> one row per account: gap-filled monthly bucket array + audit
build_deterioration   sequences -> one row per account in the segment: state + features

Nothing is dropped silently: every account in the history gets a sequences row with a
`build_status`; the classifier keeps only status 'ok' and the segment's current buckets.
"""
from __future__ import annotations

import datetime as _dt
import logging
import sys
from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

LOG = logging.getLogger(__name__)


# --- bucket schemes ----------------------------------------------------------------------

@dataclass(frozen=True)
class BucketScheme:
    name: str
    offset: int        # canonical = max(native + offset, 1)
    top: int           # highest native bucket (the cap)

    @property
    def canon_top(self) -> int:
        return self.top + self.offset

    def native_buckets(self, canonical) -> list[int]:
        """Native bucket values whose canonical value is in `canonical`."""
        return [n for n in range(self.top + 1) if max(n + self.offset, 1) in set(canonical)]


CC = BucketScheme("cc", offset=0, top=9)
RL = BucketScheme("rl", offset=1, top=7)

# Segments on the canonical scale.
SEGMENTS = {
    "60_180": (4, 5, 6, 7),      # CC native 4-7, RL native 3-6
    "180_plus": (8, 9),          # CC native 8-9, RL native 7
}


# --- parameters ----------------------------------------------------------------------------

# Read from params:crx_persona -> dpd_journey (all optional). persona_end_date is required.
PARAM_DEFAULTS = {
    # CC only, TEMPORARY: billing history before this date has known data-quality issues.
    # Set to null once the source is fixed. RL history is trusted in full.
    "cc_history_floor_date": "2024-01-01",
    "rl_history_floor_date": None,
    "segment": "60_180",                  # "60_180" or "180_plus" (the run's spine)
    "on_unresolvable_gap": "truncate",    # "truncate" (keep months after the gap) or "drop"
    "fill_straight_roll_gaps": True,      # 3 _ 5 -> 3 4 5: the only path without a +2 jump
    "repair_cycle_shift": True,           # two bills in one month + empty neighbour month
    "max_inferred_gap_months": 2,         # shorter ambiguous gaps are inferred (0 = never)
    "log_stats": False,                   # one extra aggregate job per node when True
}


@dataclass(frozen=True)
class JourneyParams:
    end_date: str
    floor_date: str | None
    segment: str
    on_unresolvable_gap: str
    fill_straight_roll_gaps: bool
    repair_cycle_shift: bool
    max_inferred_gap_months: int
    log_stats: bool


def journey_params(crx_persona: dict, scheme: BucketScheme) -> JourneyParams:
    given = crx_persona.get("dpd_journey") or {}
    unknown = sorted(set(given) - set(PARAM_DEFAULTS))
    if unknown:          # a stale key (e.g. the removed det_option) must not be silently ignored
        raise ValueError(f"dpd_journey: unknown parameter(s) {unknown}; allowed {sorted(PARAM_DEFAULTS)}")
    p = {**PARAM_DEFAULTS, **given}
    if p["segment"] not in SEGMENTS:
        raise ValueError(f"dpd_journey.segment must be one of {list(SEGMENTS)}, got {p['segment']!r}")
    if p["on_unresolvable_gap"] not in ("truncate", "drop"):
        raise ValueError("dpd_journey.on_unresolvable_gap must be 'truncate' or 'drop'")
    return JourneyParams(
        end_date=str(crx_persona["persona_end_date"]),
        floor_date=p[f"{scheme.name}_history_floor_date"],
        segment=p["segment"],
        on_unresolvable_gap=p["on_unresolvable_gap"],
        fill_straight_roll_gaps=bool(p["fill_straight_roll_gaps"]),
        repair_cycle_shift=bool(p["repair_cycle_shift"]),
        max_inferred_gap_months=int(p["max_inferred_gap_months"] or 0),
        log_stats=bool(p["log_stats"]),
    )


def _month_idx(d) -> int:
    """Month as an integer (year * 12 + month - 1) — gap arithmetic without date math."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.year * 12 + d.month - 1


# =========================================================================================
# Per-account core — plain Python, no Spark / numpy / pandas (runs inside the UDFs).
# Lists run OLDEST -> NEWEST on the canonical scale. Port of the numpy reference.
# =========================================================================================

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


def encode(b_canon: list[int]) -> tuple[list[int], list[int], list[int]]:
    """(b, d, c): repaired buckets, month-on-month change, transition code N/R/H/P."""
    b = _repair(_glitches([max(x, 1) for x in b_canon])[0])[0]
    d = [b[t + 1] - b[t] for t in range(len(b) - 1)]
    c = []
    for t, x in enumerate(d):
        cur = b[t + 1]
        if x == 0:
            c.append(N if cur == 1 else H)
        elif x < 0:
            c.append(P)
        else:
            c.append(R)                       # +1 and any leftover +2 read as a roll
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


def journey_features(b_canon: list[int], canon_top: int = 9) -> dict:
    """features.py::journey_features on a canonical bucket list (oldest -> newest).
    canon_top: the ceiling bucket (CC 9, RL 7 -> 8). A hold AT the ceiling is not a payment
    (the bucket cannot rise), so it is not counted in spell_pay_events."""
    raw = [max(x, 1) for x in b_canon]
    g, n_glitches = _glitches(raw)
    _, n_repaired, n_jumps_left = _repair(g)
    b, d, c = encode(b_canon)
    if b[-1] < 2:
        raise ValueError("not in a delinquent spell (current bucket < 2)")
    paid = [max(1 - x, 0) for x in d]

    episodes = _runs([x >= 2 for x in b])
    sp_start, sp_end = episodes[-1]
    is_blip = [e - s <= 2 and max(b[s:e]) <= 2 for s, e in episodes[:-1]]
    prior = [ep for ep, blip in zip(episodes[:-1], is_blip) if not blip]
    first_spell = (prior + [episodes[-1]])[0][0]

    def gap_prior(peak: int) -> int:
        ends = [e for s, e in prior if max(b[s:e]) >= peak]
        return sp_start - ends[-1] if ends else NO_PRIOR

    t0 = max(sp_start - 1, 0)
    sp_c = c[t0:sp_end - 1]
    hold_runs = [e - s for s, e in _runs([x == H for x in sp_c])]
    first4 = sp_start + next((i for i, x in enumerate(b[sp_start:sp_end]) if x >= 4), 0)
    ru_c = c[t0:first4]
    months_since_4 = len(b) - 1 - first4
    w0 = max(len(c) - 6, t0)
    w_c = c[w0:]
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
        "spell_pay_events": sum(1 for t in range(t0, sp_end - 1)
                                if c[t] != R and not (c[t] == H and b[t + 1] >= canon_top)),
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


# --- the state tree (states.py, option B) — ONE tree for 60-180 and 180+ -------------------

STATE_RULES = {
    "epd_max_history": 3,                # [business] months of history before the spell (blip incl.)
    "epd_max_blips": 1,                  # [business]
    "straight_max_runup": 3,             # last clean month -> first month at 4
    "stabilized_min_in_band": 5,         # [business] of the last 6 months within today's bucket ±1
    "stabilized_long_run_months": 6,     # [business]
    "stabilized_long_run_max_rise": 1,   # [business]
    "stabilized_max_bucket": 7,          # [business] canonical: CC 7 / RL 6 = 151-180 DPD. Never at 180+.
    "repeat_min_prior_peak": 3,          # [business] earlier spell reached bucket 3 ...
    "repeat_window_months": 12,          # [business] ... and ended <= 12 months before this one
    "seasoned_min_months": 12,           # [business] months on book before the spell
}

STATES = ["unknown", "early_payment_default", "stabilized", "repeat_delinquent",
          "straight_roller_seasoned", "straight_roller_early_life", "slow_roller"]

DISPLAY_NAMES = {
    "unknown": "Unknown — start of the delinquency journey not observed",
    "early_payment_default": "Early payment default (EPD)",
    "stabilized": "Stabilized",
    "repeat_delinquent": "Repeat delinquent (re-default)",
    "straight_roller_seasoned": "Seasoned straight roller",
    "straight_roller_early_life": "Early-life straight roller",
    "slow_roller": "Slow roller (partial payer)",
}


def assign_state(f: dict, cropped: bool) -> str:
    """One state per account, same tree and vocabulary in both segments. First 'yes' wins.

    Q0 journey start not observed (oldest observed month delinquent) -> stabilized if Q2, else unknown
    Q1 early payment default   <=3 months before the spell, <=1 blip, no earlier spell, no payment
                               in the spell (holds at the ceiling are not payments), not cropped
    Q2 stabilized              60-180 only (today <= CC 7 / RL 6): 5 of the last 6 months within
                               today's bucket ±1, or >=6 months since first reaching 4 and at most
                               1 bucket higher than 6 months ago
    Q3 repeat delinquent       an earlier spell reached 3, cured, ended <=12 months before this one
    Q4 straight roller         run-up to 4 took <=3 months: seasoned (>=12 months on book, or
                               cropped = older than the window) / early life
    else slow roller
    """
    p = STATE_RULES
    stab = (f["b_now"] <= p["stabilized_max_bucket"]
            and (f["last6_in_band"] >= p["stabilized_min_in_band"]
                 or (f["months_since_4"] >= p["stabilized_long_run_months"]
                     and f["chg_6m"] <= p["stabilized_long_run_max_rise"])))
    if f["starts_delinquent"]:
        return "stabilized" if stab else "unknown"
    if (f["months_before_spell"] <= p["epd_max_history"] and f["n_blips"] <= p["epd_max_blips"]
            and f["n_prior_episodes"] == 0 and f["spell_pay_events"] == 0 and not cropped):
        return "early_payment_default"
    if stab:
        return "stabilized"
    if f["gap_prior_peak3"] <= p["repeat_window_months"]:
        return "repeat_delinquent"
    if f["runup_len"] <= p["straight_max_runup"]:
        if f["months_before_spell"] >= p["seasoned_min_months"] or cropped:
            return "straight_roller_seasoned"
        return "straight_roller_early_life"
    return "slow_roller"


# --- Stage 1 core: monthly grid from raw rows ----------------------------------------------

def _legacy_drop(best: dict[int, tuple[int, int]]) -> bool:
    """Would the old window-function rule have dropped this account? (any interior gap whose
    neighbours differ in NATIVE value, after keeping the latest row per month). Lets the
    first run reconcile with the old drop count."""
    ms = sorted(best)
    return any(b - a > 1 and best[a][1] != best[b][1] for a, b in zip(ms, ms[1:]))


def build_history(rows, first_raw_idx: int, global_min_idx: int, offset: int,
                  fill_straight: bool = True, on_unresolvable: str = "truncate",
                  repair_cycle_shift: bool = True, max_inferred_gap: int = 2) -> dict:
    """rows: (month_idx, day_ordinal, native_bucket) inside [floor, end], valid buckets only.

    1. billing-cycle shift: a month with two bills next to an EMPTY interior month gives one
       bill to that month (cycle date near month-end: bills on 31 Jan and 1 Mar, none in
       Feb -> the 1 Mar bill is February's). The earlier bill moves back if the previous
       month is empty, else the later bill moves forward;
    2. one value per month: the latest observation in the month (ties -> worst bucket);
    3. dense grid from the first to the last observed month; a gap is filled when
       a. both neighbours agree on the canonical scale (hold / clean through; CC 0 = 1), or
       b. the only path without a +2 jump is a straight roll (3 _ 5 -> 3 4 5), or
       c. it is short (<= max_inferred_gap months): inferred — carry the left value and
          roll as late as possible (3 _ 4 -> 3 3 4; 5 _ 3 -> 5 5 3). Counted separately;
    4. any other gap is unresolvable: keep the months after the last one ('truncate', the
       history is then cropped) or drop the account ('drop');
    5. cropped = older history exists but is not used (history floor, truncation), or the
       first month is the first month of the whole source (opening date unknown).
    """
    out = {"build_status": "ok", "first_month_idx": None, "last_month_idx": None, "buckets": None,
           "history_cropped": None, "n_gap_months_filled": 0, "n_gap_months_rolled": 0,
           "n_gap_months_inferred": 0, "n_months_truncated": 0, "n_dup_month_rows": 0,
           "n_cycle_shift_moves": 0, "legacy_drop": False}
    by_month: dict[int, list[tuple[int, int]]] = {}
    for m, day, bkt in rows or []:
        by_month.setdefault(m, []).append((day, bkt))
    if not by_month:
        out["build_status"] = "no_rows_in_window"
        return out
    out["legacy_drop"] = _legacy_drop({m: max(v) for m, v in by_month.items()})

    if repair_cycle_shift:
        lo, hi = min(by_month), max(by_month)
        for m in sorted(by_month):
            obs = sorted(set(by_month[m]))
            days = sorted({d for d, _ in obs})
            if len(days) < 2:
                continue
            if lo < m - 1 and m - 1 not in by_month:
                by_month[m - 1] = [x for x in obs if x[0] == days[0]]
                by_month[m] = [x for x in obs if x[0] != days[0]]
                out["n_cycle_shift_moves"] += 1
            elif m + 1 < hi and m + 1 not in by_month:
                by_month[m + 1] = [x for x in obs if x[0] == days[-1]]
                by_month[m] = [x for x in obs if x[0] != days[-1]]
                out["n_cycle_shift_moves"] += 1

    best = {m: max(v) for m, v in by_month.items()}       # latest day, then worst bucket
    out["n_dup_month_rows"] = sum(len(v) for v in by_month.values()) - len(best)
    first, last = min(best), max(best)
    vals = [best[m][1] if m in best else None for m in range(first, last + 1)]
    canon = lambda x: max(x + offset, 1)          # noqa: E731
    cut = 0                                        # index of the first month kept
    filled, rolled, inferred = [], [], []          # indexes of filled months, by rule
    i = 0
    while i < len(vals):
        if vals[i] is not None:
            i += 1
            continue
        j = i
        while vals[j] is None:                     # last month is observed: always stops
            j += 1
        left, right, k = vals[i - 1], vals[j], j - i
        if canon(left) == canon(right):            # CC 0 _ 1 is clean-through, not a conflict
            vals[i:j] = [left] * k
            filled += range(i, j)
        elif fill_straight and canon(right) - canon(left) == k + 1:
            vals[i:j] = [canon(left) + s + 1 - offset for s in range(k)]
            rolled += range(i, j)
        elif k <= max_inferred_gap:
            cl, cr = canon(left), canon(right)
            vals[i:j] = [(max(cl, cr - (k - s)) if cr > cl else cl) - offset for s in range(k)]
            vals[i:j] = [max(v, 0) for v in vals[i:j]]
            inferred += range(i, j)
        else:
            if on_unresolvable == "drop":
                out["build_status"] = "dropped_unresolvable_gap"
                return out
            cut = j
        i = j
    out["n_gap_months_filled"] = sum(1 for t in filled if t >= cut)    # counted in the kept part
    out["n_gap_months_rolled"] = sum(1 for t in rolled if t >= cut)
    out["n_gap_months_inferred"] = sum(1 for t in inferred if t >= cut)
    out["n_months_truncated"] = cut
    kept_first = first + cut
    out.update(first_month_idx=kept_first, last_month_idx=last, buckets=vals[cut:],
               history_cropped=bool(kept_first > first_raw_idx or first_raw_idx <= global_min_idx))
    return out


# --- Stage 2 core: classify one account -------------------------------------------------

def classify(buckets_native: list[int], cropped: bool, offset: int, canon_top: int) -> dict:
    """Features + state for one account (native buckets, oldest -> newest)."""
    f = journey_features([max(x + offset, 1) for x in buckets_native], canon_top)
    f["det_state"] = assign_state(f, cropped)
    return f


# =========================================================================================
# Spark side
# =========================================================================================

def _ship_by_value() -> None:
    """Pickle this module's functions BY VALUE into the UDFs, so executors do not need the
    Kedro project installed (cloudpickle >= 2.0, bundled with PySpark >= 3.3). If the
    project is installed on the executors this is harmless."""
    try:
        from pyspark import cloudpickle
        if hasattr(cloudpickle, "register_pickle_by_value") and __name__ in sys.modules \
                and __name__ != "__main__":
            cloudpickle.register_pickle_by_value(sys.modules[__name__])
    except Exception as exc:  # pragma: no cover — older PySpark: needs the package on executors
        LOG.warning("could not register %s for pickle-by-value (%s); the package must be "
                    "importable on the executors", __name__, exc)


_HISTORY_SCHEMA = T.StructType([
    T.StructField("build_status", T.StringType()),
    T.StructField("first_month_idx", T.IntegerType()),
    T.StructField("last_month_idx", T.IntegerType()),
    T.StructField("buckets", T.ArrayType(T.IntegerType())),
    T.StructField("history_cropped", T.BooleanType()),
    T.StructField("n_gap_months_filled", T.IntegerType()),
    T.StructField("n_gap_months_rolled", T.IntegerType()),
    T.StructField("n_gap_months_inferred", T.IntegerType()),
    T.StructField("n_cycle_shift_moves", T.IntegerType()),
    T.StructField("legacy_drop", T.BooleanType()),
    T.StructField("n_months_truncated", T.IntegerType()),
    T.StructField("n_dup_month_rows", T.IntegerType()),
])

# Output features (name, type). Order = output column order after det_state*.
_FEATURES = [
    ("n_gap_months_filled", None), ("left_censored", T.BooleanType()),
    ("starts_delinquent", T.BooleanType()),
    ("months_before_spell", T.IntegerType()), ("n_blips", T.IntegerType()),
    ("n_prior_episodes", T.IntegerType()), ("gap_prior_peak3", T.IntegerType()),
    ("spell_pay_events", T.IntegerType()), ("runup_len", T.IntegerType()),
    ("runup_pays", T.IntegerType()), ("last6_in_band", T.IntegerType()),
    ("months_since_4", T.IntegerType()), ("chg_6m", T.IntegerType()),
    ("n_glitches", T.IntegerType()), ("n_jumps_repaired", T.IntegerType()),
    ("n_jumps_left", T.IntegerType()),
]
_CLASSIFY_SCHEMA = T.StructType([T.StructField("det_state", T.StringType())]
                                + [T.StructField(n, t) for n, t in _FEATURES if t is not None])


def _month_col(c) -> F.Column:
    return (F.year(c) * 12 + F.month(c) - 1).cast("int")


def _idx_to_month_end(c) -> F.Column:
    return F.last_day(F.expr("make_date(cast({0} div 12 as int), cast({0} % 12 + 1 as int), 1)".format(c)))


def build_dpd_sequences(history: DataFrame, scheme: BucketScheme, params: JourneyParams,
                        restructure: DataFrame | None = None) -> DataFrame:
    """history: account_id, obs_date (date/timestamp), dlq_bucket (native int),
    optionally restructure_flag (0/1 per row; max over the account's rows).
    restructure: optional (account_id, restructure_blind_spot_flag), one row per account.

    Returns ONE row per account (every account in `history`, with a build_status):
        account_id, build_status, first_month, last_month (month-end dates),
        history_months, dlq_buckets array<int> (native, oldest -> newest, gap-filled),
        dpd_string (native digits, LEFTMOST = latest month — the bank's string convention),
        history_cropped, n_gap_months_filled, n_gap_months_rolled, n_gap_months_inferred,
        n_cycle_shift_moves, n_months_truncated, n_dup_month_rows, n_invalid_rows,
        legacy_drop (the old rule would have dropped it), restructure_blind_spot_flag
    """
    missing = [c for c in ("account_id", "obs_date", "dlq_bucket") if c not in history.columns]
    if missing:
        raise ValueError(f"build_dpd_sequences: history is missing {missing}; has {sorted(history.columns)}")
    _ship_by_value()
    end_dt = F.to_date(F.lit(params.end_date))
    floor_idx = _month_idx(params.floor_date) if params.floor_date else None

    m = _month_col(F.col("obs_date"))
    bucket = F.col("dlq_bucket").cast("int")
    valid = bucket.isNotNull() & bucket.between(0, scheme.top)
    in_window = valid if floor_idx is None else valid & (m >= F.lit(floor_idx))
    h = history.where(F.col("obs_date").cast("date") <= end_dt)

    aggs = [
        F.collect_list(F.when(in_window, F.struct(
            m.alias("m"),
            F.datediff(F.col("obs_date").cast("date"), F.lit("1970-01-01")).alias("d"),
            bucket.alias("b"),
        ))).alias("_rows"),
        F.min(F.when(valid, m)).alias("_first_raw"),
        F.sum((~valid).cast("int")).alias("n_invalid_rows"),   # null / out-of-range buckets
    ]
    if "restructure_flag" in history.columns:
        aggs.append(F.max(F.col("restructure_flag").cast("int")).alias("_rf"))
    per_acc = h.groupBy("account_id").agg(*aggs)                       # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))     # 1 row
    per_acc = per_acc.crossJoin(F.broadcast(source_min))

    offset, fill, how = scheme.offset, params.fill_straight_roll_gaps, params.on_unresolvable_gap
    shift, max_inf = params.repair_cycle_shift, params.max_inferred_gap_months

    def _udf(rows, first_raw, global_min):
        if first_raw is None:
            return {"build_status": "no_valid_rows"}
        return build_history([(r["m"], r["d"], r["b"]) for r in rows], first_raw, global_min,
                             offset, fill, how, shift, max_inf)

    hist_udf = F.udf(_udf, _HISTORY_SCHEMA)
    s = per_acc.withColumn("_h", hist_udf("_rows", "_first_raw", "_global_min"))

    out = s.select(
        "account_id",
        F.col("_h.build_status").alias("build_status"),
        _idx_to_month_end("_h.first_month_idx").alias("first_month"),
        _idx_to_month_end("_h.last_month_idx").alias("last_month"),
        F.size("_h.buckets").alias("history_months"),
        F.col("_h.buckets").alias("dlq_buckets"),
        F.concat_ws("", F.reverse(F.col("_h.buckets").cast("array<string>"))).alias("dpd_string"),
        F.col("_h.history_cropped").alias("history_cropped"),
        F.coalesce("_h.n_gap_months_filled", F.lit(0)).alias("n_gap_months_filled"),
        F.coalesce("_h.n_gap_months_rolled", F.lit(0)).alias("n_gap_months_rolled"),
        F.coalesce("_h.n_gap_months_inferred", F.lit(0)).alias("n_gap_months_inferred"),
        F.coalesce("_h.n_cycle_shift_moves", F.lit(0)).alias("n_cycle_shift_moves"),
        F.coalesce("_h.legacy_drop", F.lit(False)).alias("legacy_drop"),
        F.coalesce("_h.n_months_truncated", F.lit(0)).alias("n_months_truncated"),
        F.coalesce("_h.n_dup_month_rows", F.lit(0)).alias("n_dup_month_rows"),
        F.col("n_invalid_rows").cast("int"),
        (F.col("_rf") if "_rf" in s.columns else F.lit(None).cast("int")).alias("_rf"),
    )
    if restructure is not None:
        out = out.join(restructure.select("account_id", F.col("restructure_blind_spot_flag").alias("_rs")),
                       "account_id", "left")
        flag = F.greatest(F.coalesce("_rf", F.lit(0)), F.coalesce("_rs", F.lit(0)))
    else:
        flag = F.coalesce("_rf", F.lit(0))
    out = out.withColumn("restructure_blind_spot_flag", flag.cast("int")).drop("_rf", "_rs")
    if params.log_stats:
        out = out.persist()
        _log_sequence_stats(out, scheme, params)
    return out


def build_deterioration(sequences: DataFrame, scheme: BucketScheme, params: JourneyParams) -> DataFrame:
    """sequences: output of build_dpd_sequences. Keeps build_status 'ok' and accounts whose
    LATEST month is in the segment (native buckets), and assigns one state per account.

    Returns one row per account:
        account_id, det_state, det_state_label, det_segment, current_bucket
        (native), <features>, history_months, history_cropped, n_months_truncated,
        history_stale_months (snapshot month - last observed month), restructure_blind_spot_flag,
        computed_at
    """
    _ship_by_value()
    segment = params.segment
    native = scheme.native_buckets(SEGMENTS[segment])
    cur = F.element_at("dlq_buckets", -1)
    seg = sequences.where((F.col("build_status") == "ok") & cur.isin(native))

    offset, top = scheme.offset, scheme.canon_top

    def _udf(buckets, cropped):
        return classify(list(buckets), bool(cropped), offset, top)

    schema = _CLASSIFY_SCHEMA
    res = seg.withColumn("_s", F.udf(_udf, schema)("dlq_buckets", "history_cropped"))

    labels = F.create_map(*[F.lit(x) for kv in DISPLAY_NAMES.items() for x in kv])
    snap = _month_idx(params.end_date)
    feat_cols = [F.col(f"_s.{f.name}").alias(f.name) for f in schema.fields if f.name != "det_state"]
    out = res.select(
        F.col("account_id"),
        F.col("_s.det_state").alias("det_state"),
        labels[F.col("_s.det_state")].alias("det_state_label"),
        F.lit(segment).alias("det_segment"),
        cur.alias("current_bucket"),
        F.col("n_gap_months_filled"),
        *feat_cols,
        F.col("history_months"),
        F.col("history_cropped"),
        F.col("n_months_truncated"),
        (F.lit(snap) - _month_col(F.col("last_month"))).alias("history_stale_months"),
        F.col("restructure_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    if params.log_stats:
        out = out.persist()
        _log_state_stats(sequences, out, scheme, params)
    return out


# --- logging (opt-in: each call is one aggregate job) ------------------------------------------

def _log_sequence_stats(seq: DataFrame, scheme: BucketScheme, params: JourneyParams) -> None:
    r = seq.agg(
        F.count("*").alias("accounts"),
        *[F.sum((F.col("build_status") == s).cast("int")).alias(s)
          for s in ("ok", "no_rows_in_window", "no_valid_rows", "dropped_unresolvable_gap")],
        F.sum(F.col("history_cropped").cast("int")).alias("cropped"),
        F.sum((F.col("n_months_truncated") > 0).cast("int")).alias("truncated_accounts"),
        F.sum("n_gap_months_filled").alias("gap_months_filled"),
        F.sum("n_gap_months_rolled").alias("gap_months_rolled"),
        F.sum("n_gap_months_inferred").alias("gap_months_inferred"),
        F.sum("n_cycle_shift_moves").alias("cycle_shift_moves"),
        F.sum(F.col("legacy_drop").cast("int")).alias("legacy_rule_would_drop"),
        F.sum("n_dup_month_rows").alias("dup_month_rows"),
        F.sum("n_invalid_rows").alias("invalid_rows"),
        F.min("first_month").alias("first_month"),
        F.max("last_month").alias("last_month"),
    ).first().asDict()
    LOG.info("build_%s_dpd_sequences [end %s, floor %s, gaps %s]: %s",
             scheme.name, params.end_date, params.floor_date, params.on_unresolvable_gap, r)


def _log_state_stats(seq: DataFrame, out: DataFrame, scheme: BucketScheme, params: JourneyParams) -> None:
    n_ok = seq.where(F.col("build_status") == "ok").count()
    rows = out.groupBy("det_state").count().orderBy(F.desc("count")).collect()
    n = sum(r["count"] for r in rows) or 1
    LOG.info("build_%s_deterioration [%s]: %d of %d ok accounts in segment; %s", scheme.name,
             params.segment, n, n_ok,
             ", ".join(f"{r['det_state']} {r['count']} ({r['count'] / n:.1%})" for r in rows))
