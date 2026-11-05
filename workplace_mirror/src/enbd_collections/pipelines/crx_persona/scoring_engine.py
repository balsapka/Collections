"""Points -> state scoring shared by the axes (A1; A3 next). An axis declares a
``Scorecard`` (dimensions with points per level, thresholds, overrides, state labels)
and builds its own level columns; ``Scorecard.score`` adds points, state, the override
that fired and the reason. Imported by the axes; not run on its own."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

DEMOTE, CAP, FORCE = "demote", "cap", "force"  # Override modes
RUNGS = ("low", "moderate", "high")


@dataclass(frozen=True)
class Dimension:
    """A scored dimension: its ``level`` column, the points per level (others 0; may be
    negative) and the ``silent`` levels that mean "no evidence" (the Unknown gate)."""

    name: str
    level: str
    points: Mapping[str, int]
    silent: tuple[str, ...] = ("none",)


@dataclass(frozen=True)
class Override:
    """A boolean ``flag`` column that, when true, moves the state: ``DEMOTE`` one rung
    (never below Low), ``CAP`` at rung ``to``, or ``FORCE`` to rung ``to``."""

    name: str
    flag: str
    mode: str = DEMOTE
    to: str = "low"


@dataclass(frozen=True)
class Scorecard:  # pylint: disable=too-many-instance-attributes,too-many-locals
    """Points over ``dimensions`` -> High / Moderate / Low, overrides, an Unknown gate.

    Rungs from the points total (``high_from`` / ``moderate_from``, inclusive); High
    also needs ``high_min_dimensions`` dimensions with points, one in ``high_current``
    if given, else Moderate. The first override whose flag is true, in declared order,
    moves the rung (no stacking; a NULL flag does not fire). Unknown: every level silent
    or NULL, no override, and ``unknown_also``. ``labels``: rung or "unknown" -> value.
    """

    prefix: str
    dimensions: tuple[Dimension, ...]
    labels: Mapping[str, str]
    high_from: int
    moderate_from: int
    overrides: tuple[Override, ...] = ()
    high_min_dimensions: int = 0
    high_current: tuple[str, ...] = ()

    def score(self, df: DataFrame, unknown_also: Column | None = None) -> DataFrame:
        """``df`` + ``<prefix>_<dimension>_points``, ``_points_total``, ``_state``,
        ``_override`` (the one that fired), ``_reason`` (it, else the top dimension)."""
        p = self.prefix
        pts = {
            d.name: F.coalesce(state_label(d.level, d.points), F.lit(0))
            for d in self.dimensions
        }
        total = sum(pts.values())
        scored = sum((c > 0).cast("int") for c in pts.values())
        high = (total >= self.high_from) & (scored >= self.high_min_dimensions)
        if self.high_current:
            high &= F.array_max(F.array(*[pts[n] for n in self.high_current])) > 0
        rung = F.when(high, 2).when(total >= self.moderate_from, 1).otherwise(0)
        fired = F.coalesce(
            *[F.when(F.col(o.flag), F.lit(o.name)) for o in self.overrides],
            F.lit(None).cast("string"),
        )
        for o in self.overrides:
            to = F.lit(RUNGS.index(o.to))
            moved = {DEMOTE: F.greatest(rung - 1, F.lit(0)), CAP: F.least(rung, to)}
            rung = F.when(fired == o.name, moved.get(o.mode, to)).otherwise(rung)
        unknown = F.lit(True) if unknown_also is None else unknown_also
        unknown &= fired.isNull()
        for d in self.dimensions:
            unknown &= F.coalesce(F.col(d.level).isin(*d.silent), F.lit(True))
        state = F.when(unknown, self.labels["unknown"])
        for i in (2, 1):
            state = state.when(rung == i, self.labels[RUNGS[i]])
        ranked = [
            F.struct(c.alias("pts"), F.lit(-i).alias("i"), F.lit(n).alias("n"))
            for i, (n, c) in enumerate(pts.items())
        ]
        top = F.sort_array(F.array(*ranked), asc=False)[0]  # ties: declared order
        return df.select(
            "*",
            *[c.alias(f"{p}_{n}_points") for n, c in pts.items()],
            total.alias(f"{p}_points_total"),
            state.otherwise(self.labels["low"]).alias(f"{p}_state"),
            fired.alias(f"{p}_override"),
            F.coalesce(fired, F.when(top["pts"] > 0, top["n"])).alias(f"{p}_reason"),
        )


def state_label(col: str, labels: Mapping[str, object]) -> Column:
    """The ``labels`` value of each ``col`` value; NULL for a value ``labels`` lacks."""
    return F.create_map(*[F.lit(x) for kv in labels.items() for x in kv])[F.col(col)]
