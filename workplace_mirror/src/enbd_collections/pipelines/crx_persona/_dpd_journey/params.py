"""Run parameters: defaults, the resolved dataclass, and the merge/validate entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import BucketScheme, MODEL_ID_SEGMENT

# Read from params:crx_persona -> dpd_journey (all optional). persona_end_date is required.
PARAM_DEFAULTS = {
    # CC only, TEMPORARY: billing history before this date has known data-quality issues.
    # Set to null once the source is fixed. RL history is trusted in full.
    "cc_history_floor_date": "2024-01-01",
    # Independently overridable for the 180_plus segment (T43 2026-10-20 PROD run: the
    # shared floor left 99.07% of the gt2y chargeoff-age vintage "unknown" — their journey
    # start is almost always before the floor by construction). Defaults to the same value
    # as cc_history_floor_date so today's output is unchanged; override to relax/remove the
    # floor for 180_plus once the pre-2024 data-quality tradeoff is decided.
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
    segment is derived from model_id (MODEL_ID_SEGMENT) — not an overridable param."""
    given = crx_persona.get("dpd_journey") or {}
    unknown = sorted(set(given) - set(PARAM_DEFAULTS))
    # a stale key (e.g. the removed det_option, or a removed segment override) must not
    # be silently ignored
    if unknown:
        raise ValueError(
            f"dpd_journey: unknown parameter(s) {unknown}; allowed {sorted(PARAM_DEFAULTS)}"
        )
    p = {**PARAM_DEFAULTS, **given}
    if model_id not in MODEL_ID_SEGMENT:
        raise ValueError(
            f"model_id must be one of {sorted(MODEL_ID_SEGMENT)}, got {model_id!r}"
        )
    segment = MODEL_ID_SEGMENT[model_id]
    if p["on_unresolvable_gap"] not in ("truncate", "drop"):
        raise ValueError("dpd_journey.on_unresolvable_gap must be 'truncate' or 'drop'")
    floor_key = (
        "cc_history_floor_date_180_plus"
        if scheme.name == "cc" and segment == "180_plus"
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
