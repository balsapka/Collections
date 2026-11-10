"""TEMPORARY (A1 bundle 21): the evidence-family rule against the A1 output persisted
before it (bundle 14 rule: income + liquidity), all persona months.

The check runs the new A1 pipeline into ``crx_<p>_a1_check_new`` (the real output is
untouched) and logs, for the latest month:

- ``A1 OUTPUT``: new and old state mix, the reason and unknown-reason mix;
- ``A1 MOVES``: old x new states;
- ``A1 FAMILIES``: each family's levels, strong families per row, the balance in money in
  (rows it makes strong, the states it moves) and the sweepable-balance flag;
- ``A1 OUTCOMES`` (60_180): cure / pay / roll by new state over the Jan–May cohort.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a1_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals

import logging

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, window_months
from .classify import FAMILIES, MONEY_IN_SOME, SCORECARD, _flow_level
from .pipeline import TAGS, create_a1_pipeline

logger = logging.getLogger(__name__)
LEVEL_COLS = [dimension.level for _, dimension in FAMILIES]


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _latest(df: DataFrame, persona_end_date: str) -> DataFrame:
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return df.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], total: int) -> list[str]:
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "  "
        + " | ".join(str(r[c]) for c in cols)
        + f": {r['count']} ({100 * r['count'] / max(total, 1):.1f}%)"
        for r in rows
    ]


def _without_balance(new: DataFrame, casa: DataFrame, model_id: str) -> DataFrame:
    """``new`` + ``state_no_balance``: the state when the CASA balance does not count
    towards money in (money in = the inflow level alone)."""
    w = window_months(model_id)
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    df = new.join(casa, on=list(GRAIN), how="left").withColumn(
        "_inflow", _flow_level("in", MONEY_IN_SOME, amt, w)
    )
    rescored = SCORECARD.score(
        df.withColumn(
            "a1_money_in_level",
            F.when(F.col("a1_sweepable_balance_flag") == 1, F.col("_inflow")).otherwise(
                F.col("a1_money_in_level")
            ),
        )
        .withColumn("a1_distress_flag", F.col("a1_distress_flag") == 1)
        .drop("a1_state", "a1_points_total", "a1_reason"),
        unknown_also=F.coalesce(F.col("casa_active"), F.lit(0)) == 0,
    )
    return rescored.select(
        *GRAIN,
        F.col("a1_state").alias("state_no_balance"),
        (
            (F.col("a1_sweepable_balance_flag") == 1)
            & (F.coalesce(F.col("_inflow"), F.lit("")) != "strong")
        )
        .cast("int")
        .alias("balance_only_strong"),
    )


def cohort_outcome_lines(new: DataFrame, model_id: str) -> list[str]:
    """``cure_3`` / ``pay_any_3`` / ``roll_3`` (%) by new A1 state over the Jan–May 2026
    cohort, n per state, 60_180 only.

    TODO(sonnet): implement with the round-3 snippet's outcome definitions
    (``tmp_validation/a1_family_redesign/round3_snippet.py``: the same cohort, the same
    three outcomes, raw and DPD-band standardised, with 95% intervals), adding the
    catalog datasets it needs as node inputs of ``compare_a1``. Aggregates only.
    """
    if "60_180" not in model_id:
        return ["  180+: no outcomes (as in rounds 1-3)"]
    del new
    return ["  TODO(sonnet): cohort outcomes not implemented"]


def compare_a1(
    old: DataFrame,
    new: DataFrame,
    casa: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """Logs the A1 OUTPUT / MOVES / FAMILIES / OUTCOMES blocks for ``model_id``."""
    head = [f"  model_id {model_id}, latest month {persona_end_date}"]
    new_l = _latest(new, persona_end_date).cache()
    old_l = _latest(old, persona_end_date).select(
        *GRAIN, F.col("a1_state").alias("old_state")
    )
    n_new, n_old = new_l.count(), old_l.count()
    _block(
        "A1 OUTPUT",
        head
        + [f"  new rows {n_new}, old rows {n_old}", "  new state:"]
        + _counts(new_l, ["a1_state"], n_new)
        + ["  old state:"]
        + _counts(old_l, ["old_state"], n_old)
        + ["  new reason:"]
        + _counts(new_l, ["a1_reason"], n_new)
        + ["  new unknown reason (unknown rows):"]
        + _counts(
            new_l.filter(F.col("a1_state") == "unknown"), ["a1_unknown_reason"], n_new
        ),
    )
    moves = old_l.join(new_l.select(*GRAIN, "a1_state"), on=list(GRAIN), how="full")
    _block(
        "A1 MOVES",
        head + ["  old | new"] + _counts(moves, ["old_state", "a1_state"], n_new),
    )
    top = ["stable"] + ["strong"] * (len(LEVEL_COLS) - 1)
    strong = sum(
        F.coalesce(F.col(c) == lvl, F.lit(False)).cast("int")
        for c, lvl in zip(LEVEL_COLS, top)
    )
    nb = _without_balance(new_l, _latest(casa, persona_end_date), model_id).cache()
    families = head[:]
    for col in LEVEL_COLS:
        families += [f"  {col}:"] + _counts(new_l, [col], n_new)
    families += ["  strong families per row:"] + _counts(
        new_l.withColumn("strong_families", strong), ["strong_families"], n_new
    )
    families += ["  sweepable balance flag:"] + _counts(
        new_l, ["a1_sweepable_balance_flag"], n_new
    )
    families += ["  money in strong only through the balance:"] + _counts(
        nb, ["balance_only_strong"], n_new
    )
    moved = new_l.select(*GRAIN, "a1_state").join(nb, on=list(GRAIN))
    families += [
        "  state without the balance | with it (rows the balance moves):"
    ] + _counts(
        moved.filter(F.col("state_no_balance") != F.col("a1_state")),
        ["state_no_balance", "a1_state"],
        n_new,
    )
    _block("A1 FAMILIES", families)
    _block("A1 OUTCOMES", head + cohort_outcome_lines(new, model_id))
    new_l.unpersist()
    nb.unpersist()


def create_a1_check_pipeline(product: str, anchor: Node) -> Pipeline:
    """The new A1 pipeline into ``crx_<p>_a1_check_new``, then the comparison."""
    prefix = f"crx_{product}_a1"
    return create_a1_pipeline(product, f"{prefix}_check_new", anchor) + Pipeline(
        [
            node(
                func=compare_a1,
                inputs={
                    "old": f"{prefix}_ability",
                    "new": f"{prefix}_check_new",
                    "casa": f"{prefix}_casa_signals",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name=f"compare_{prefix}_check",
                tags=TAGS,
            )
        ]
    )
