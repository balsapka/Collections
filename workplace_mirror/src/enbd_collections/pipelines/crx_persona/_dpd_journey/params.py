"""Run parameters: defaults, the resolved dataclass, and the merge/validate entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from .._common import SEG_180_PLUS
from .._common import segment as model_segment
from .constants import BucketScheme

# Read from params:crx_persona -> dpd_journey (all optional). persona_end_date is required.
PARAM_DEFAULTS = {
    # CC only, TEMPORARY: billing history before this date has known data-quality issues.
    # Set to null once the source is fixed. RL history is trusted in full.
    "cc_history_floor_date": "2024-01-01",
    # Overridable for the 180_plus segment alone: the journey of most long charged-off
    # accounts starts before the shared floor, which leaves them "unknown". Defaults to
    # cc_history_floor_date; override to relax or remove the floor for 180_plus
    # (conformance D5).
    "cc_history_floor_date_180_plus": "2024-01-01",
    "rl_history_floor_date": None,
    "on_unresolvable_gap": "truncate",  # "truncate" (keep months after the gap) or "drop"
    "fill_straight_roll_gaps": True,  # 3 · 5 -> 3 4 5: the only path without a +2 jump
    "repair_cycle_shift": True,  # two bills in one month + empty neighbour month
    "max_inferred_gap_months": 2,  # shorter ambiguous gaps are inferred (0 = never)
    "log_stats": False,  # one extra aggregate job per node when True
}


@dataclass(frozen=True)
# pylint: disable-next=too-many-instance-attributes
class JourneyParams:
    """Resolved dpd_journey run parameters (defaults merged with crx_persona overrides)."""

    end_date: str
    floor_date: str | None
    segment: str
    on_unresolvable_gap: str
    fill_straight_roll_gaps: bool
    repair_cycle_shift: bool
    max_inferred_gap_months: int
    log_stats: bool


def journey_params(
    crx_persona: dict, scheme: BucketScheme, model_id: str
) -> JourneyParams:
    """Resolve PARAM_DEFAULTS + crx_persona["dpd_journey"] overrides into a JourneyParams.
    segment is derived from model_id (_common.segment) — not an overridable param."""
    given = crx_persona.get("dpd_journey") or {}
    unknown = sorted(set(given) - set(PARAM_DEFAULTS))
    # a stale key must not be silently ignored
    if unknown:
        raise ValueError(
            f"dpd_journey: unknown parameter(s) {unknown}; allowed {sorted(PARAM_DEFAULTS)}"
        )
    p = {**PARAM_DEFAULTS, **given}
    segment = model_segment(model_id)
    if p["on_unresolvable_gap"] not in ("truncate", "drop"):
        raise ValueError("dpd_journey.on_unresolvable_gap must be 'truncate' or 'drop'")
    floor_key = (
        "cc_history_floor_date_180_plus"
        if scheme.name == "cc" and segment == SEG_180_PLUS
        else f"{scheme.name}_history_floor_date"
    )
    return JourneyParams(
        end_date=str(crx_persona["persona_end_date"]),
        floor_date=p[floor_key],
        segment=segment,
        on_unresolvable_gap=p["on_unresolvable_gap"],
        fill_straight_roll_gaps=bool(p["fill_straight_roll_gaps"]),
        repair_cycle_shift=bool(p["repair_cycle_shift"]),
        max_inferred_gap_months=int(p["max_inferred_gap_months"] or 0),
        log_stats=bool(p["log_stats"]),
    )
