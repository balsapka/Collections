"""Points -> state-ladder primitives shared by the crx_persona axes.

N named point dimensions are summed to a total; a High/Moderate/Low(/Unknown) ladder
turns the total into a state; an override condition demotes the state by exactly one
rung (never stacks); a no-signal gate is checked first. Each axis supplies its own
dimension logic, state labels and thresholds (A1: ``a1_ability.classify``); this module
only owns the combination step.

Pure ``pyspark.sql.Column`` in, ``Column`` out, so an axis wires these into its own
node without restructuring joins. Imported by the axes; not run on its own.
"""

from dataclasses import dataclass
from typing import Mapping

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


def state_label(col: str, labels: Mapping[str, str]) -> Column:
    """The display label of each ``col`` value; NULL for a value ``labels`` lacks."""
    return F.create_map(*[F.lit(x) for kv in labels.items() for x in kv])[F.col(col)]
