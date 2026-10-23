"""Shared points -> state-ladder scoring primitives for crx_persona axes.

Pulled out after confirming T31's A1 ability v2 (cc_a1_ability_v2) and the
DE's A3 payment-credibility rewrite (cc_a3_payment_credibility) converged
independently on the same shape: N named point dimensions summed to a total,
a priority-ordered override condition that demotes the computed state by
exactly one rung (never stacks), a High/Moderate/Low(/Unknown) ladder, and a
no-signal gate checked first. Verified cell-by-cell against both real
implementations (A1 v2's MECE map and A3's ``_a3_state_col``) before this was
extracted.

Each axis supplies its own dimension logic, state label strings and point
thresholds — this module only owns the combination step. No confidence
scoring lives here; axes that need a confidence column derive it themselves
from the state (as A3 already does).

Pure ``pyspark.sql.Column`` in, ``Column`` out — no DataFrame coupling, so
either axis wires these into its own node without restructuring joins.
"""

from dataclasses import dataclass
from typing import Mapping, Sequence

from pyspark.sql import Column
from pyspark.sql import functions as F


def points_from_level(level_col: Column, points_by_level: Mapping[str, int]) -> Column:
    """Map a named level string column to its integer point value.

    ``points_by_level`` is an equality lookup, not a ladder — order doesn't
    matter. A level value not present in ``points_by_level`` (including NULL)
    falls through to 0.
    """
    expr = F.lit(0)
    for level, points in points_by_level.items():
        expr = F.when(level_col == F.lit(level), F.lit(points)).otherwise(expr)
    return expr


def priority_reason(
    conditions: Mapping[str, Column], priority_high_to_low: Sequence[str]
) -> Column:
    """Pick the single highest-priority named condition that fires, else NULL.

    ``conditions`` maps a reason name to its boolean Column. ``priority_high_to_low``
    must list every key in ``conditions``, most important first — when more
    than one condition fires for the same row, the first (highest-priority)
    match wins.
    """
    expr = F.lit(None).cast("string")
    for reason in reversed(priority_high_to_low):
        expr = F.when(conditions[reason], F.lit(reason)).otherwise(expr)
    return expr


@dataclass(frozen=True)
class StateLadder:
    """A High/Moderate/Low(/Unknown) points ladder with a one-rung override demotion.

    ``high_from_points`` / ``moderate_from_points`` are inclusive point
    thresholds for the un-demoted ladder. An override (e.g. a distress flag,
    a strong-negative reason) drops the computed level by exactly one rung —
    High -> Moderate, Moderate -> Low — and never pushes below ``low``, the
    ladder's floor. ``unknown`` is a separate gate, not reachable via points;
    the caller decides when it fires (typically "no signal from any
    dimension and no override") and passes that as ``is_unknown``.
    """

    high: str
    moderate: str
    low: str
    unknown: str
    high_from_points: int
    moderate_from_points: int

    def state(
        self, points_total: Column, has_override: Column, is_unknown: Column
    ) -> Column:
        """Combine points, the override boolean and the unknown gate into a state column.

        Unknown is checked first and short-circuits the ladder. Otherwise:
        High requires points >= high_from_points AND no override; Moderate
        fires either on points >= moderate_from_points with no override, or
        on points >= high_from_points WITH an override (the one-rung
        demotion from High); everything else is Low.
        """
        return (
            F.when(is_unknown, F.lit(self.unknown))
            .when(
                (points_total >= self.high_from_points) & (~has_override),
                F.lit(self.high),
            )
            .when(
                ((points_total >= self.moderate_from_points) & (~has_override))
                | ((points_total >= self.high_from_points) & has_override),
                F.lit(self.moderate),
            )
            .otherwise(F.lit(self.low))
        )
