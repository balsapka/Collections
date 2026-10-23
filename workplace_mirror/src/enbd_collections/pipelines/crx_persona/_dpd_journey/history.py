"""Stage 1 core: monthly grid from raw rows.

Not reference-constrained (no counterpart in the numpy reference — it is the billing-
history gap-fill stage), so unlike core.py it is free to decompose internally.
"""

from __future__ import annotations


def _legacy_drop(best: dict[int, tuple[int, int]]) -> bool:
    """Would the old window-function rule have dropped this account? (any interior gap whose
    neighbours differ in NATIVE value, after keeping the latest row per month). Lets the
    first run reconcile with the old drop count."""
    ms = sorted(best)
    return any(b - a > 1 and best[a][1] != best[b][1] for a, b in zip(ms, ms[1:]))


# pylint: disable-next=too-many-locals
def _fill_gaps(
    vals: list,
    offset: int,
    fill_straight: bool,
    on_unresolvable: str,
    max_inferred_gap: int,
) -> tuple[list, list[int], list[int], list[int], int, bool]:
    """Step 3-4 of build_history's docstring: walk `vals` (one slot per month, `None` where
    unobserved) and fill each gap — clean-through (3a), straight-roll (3b), or short inferred
    (3c) — or mark it unresolvable (4): truncate everything up to it (`cut` advances) or signal
    a drop. Returns (vals, filled, rolled, inferred, cut, dropped) — month-indexes (relative to
    `vals`) for each fill rule, the truncation cut point, and whether `on_unresolvable == "drop"`
    was hit."""

    def canon(x):
        return max(x + offset, 1)

    cut = 0  # index of the first month kept
    filled, rolled, inferred = [], [], []  # indexes of filled months, by rule
    i = 0
    while i < len(vals):
        if vals[i] is not None:
            i += 1
            continue
        j = i
        while vals[j] is None:  # last month is observed: always stops
            j += 1
        left, right, k = vals[i - 1], vals[j], j - i
        if canon(left) == canon(right):  # CC 0 · 1 is clean-through, not a conflict
            vals[i:j] = [left] * k
            filled += range(i, j)
        elif fill_straight and canon(right) - canon(left) == k + 1:
            vals[i:j] = [canon(left) + s + 1 - offset for s in range(k)]
            rolled += range(i, j)
        elif k <= max_inferred_gap:
            cl, cr = canon(left), canon(right)
            vals[i:j] = [
                (max(cl, cr - (k - s)) if cr > cl else cl) - offset for s in range(k)
            ]
            vals[i:j] = [max(v, 0) for v in vals[i:j]]
            inferred += range(i, j)
        else:
            if on_unresolvable == "drop":
                return vals, filled, rolled, inferred, cut, True
            cut = j
        i = j
    return vals, filled, rolled, inferred, cut, False


# pylint: disable-next=too-many-positional-arguments,too-many-locals,too-many-branches,too-many-statements
def build_history(
    rows,
    first_raw_idx: int,
    global_min_idx: int,
    offset: int,
    fill_straight: bool = True,
    on_unresolvable: str = "truncate",
    repair_cycle_shift: bool = True,
    max_inferred_gap: int = 2,
) -> dict:
    """rows: (month_idx, day_ordinal, native_bucket) inside [floor, end], valid buckets only.

    1. billing-cycle shift: a month with two bills next to an EMPTY interior month gives one
       bill to that month (cycle date near month-end: bills on 31 Jan and 1 Mar, none in
       Feb -> the 1 Mar bill is February's). The earlier bill moves back if the previous
       month is empty, else the later bill moves forward;
    2. one value per month: the latest observation in the month (ties -> worst bucket);
    3. dense grid from the first to the last observed month; a gap is filled when
       a. both neighbours agree on the canonical scale (hold / clean through; CC 0 · 1), or
       b. the only path without a +2 jump is a straight roll (3 · 5 -> 3 4 5), or
       c. it is short (<= max_inferred_gap months): inferred — carry the left value and
          roll as late as possible (3 · 4 -> 3 3 4; 5 · 3 -> 5 5 3). Counted separately;
    4. any other gap is unresolvable: keep the months after the last one ('truncate', the
       history is then cropped) or drop the account ('drop');
    5. cropped = older history exists but is not used (history floor, truncation), or the
       first month is the first month of the whole source (opening date unknown).
    """
    out = {
        "build_status": "ok",
        "first_month_idx": None,
        "last_month_idx": None,
        "buckets": None,
        "history_cropped": None,
        "n_gap_months_filled": 0,
        "n_gap_months_rolled": 0,
        "n_gap_months_inferred": 0,
        "n_months_truncated": 0,
        "n_dup_month_rows": 0,
        "n_cycle_shift_moves": 0,
        "legacy_drop": False,
    }
    by_month: dict[int, list[tuple[int, int]]] = {}
    for m, day, bkt in rows or []:
        by_month.setdefault(m, []).append((day, bkt))
    if not by_month:
        out["build_status"] = "no_rows_in_window"
        return out
    out["legacy_drop"] = _legacy_drop({m: max(v) for m, v in by_month.items()})

    # Step 1: billing-cycle shift.
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

    # Step 2: one value per month (latest day, then worst bucket).
    best = {m: max(v) for m, v in by_month.items()}
    out["n_dup_month_rows"] = sum(len(v) for v in by_month.values()) - len(best)
    first, last = min(best), max(best)
    vals = [best[m][1] if m in best else None for m in range(first, last + 1)]

    # Steps 3-4: dense grid + gap fill / truncate / drop.
    vals, filled, rolled, inferred, cut, dropped = _fill_gaps(
        vals, offset, fill_straight, on_unresolvable, max_inferred_gap
    )
    if dropped:
        out["build_status"] = "dropped_unresolvable_gap"
        return out
    out["n_gap_months_filled"] = sum(
        1 for t in filled if t >= cut
    )  # counted in the kept part
    out["n_gap_months_rolled"] = sum(1 for t in rolled if t >= cut)
    out["n_gap_months_inferred"] = sum(1 for t in inferred if t >= cut)
    out["n_months_truncated"] = cut

    # Step 5: cropped flag.
    kept_first = first + cut
    out.update(
        first_month_idx=kept_first,
        last_month_idx=last,
        buckets=vals[cut:],
        history_cropped=bool(
            kept_first > first_raw_idx or first_raw_idx <= global_min_idx
        ),
    )
    return out
