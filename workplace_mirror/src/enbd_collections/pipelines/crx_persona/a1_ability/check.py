"""TEMPORARY (A1 bundle 24): A1 with bureau salary from the DE's unified table against the
persisted A1 output (bureau salary from the alert feed, RL plus the loan's bureau pull).

The check rebuilds ``feat_cif_bureau_salary_monthly`` from ``feat_bureau_salary_unified``
into ``feat_cif_bureau_salary_monthly_b24_new`` and the income signals and A1 state into
``crx_<p>_a1_income_b24_new`` / ``crx_<p>_a1_b24_new``; the other signals are the persisted
ones, and no real output is touched. It logs, for the latest month's observation CIFs:

- ``B24 BUREAU``: old and new bureau rows in the last 2W + 1 months (rows, zero rows, new
  rows by ``salary_source``), CIF-months only old / only new / in both with amounts more
  than 1% apart;
- ``B24 INCOME``: old x new bureau evidence in the window, income source and income level;
- ``B24 A1 OUTPUT``: old and new state mix;
- ``B24 A1 MOVES``: old x new state.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a1_b24_check
"""

import logging

from kedro.pipeline import Pipeline, node
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.bureau import feat_cif_bureau_salary_monthly

from .._common import GRAIN, window_months
from .classify import build_a1_ability
from .pipeline import TAGS
from .signals import build_income_signals

logger = logging.getLogger(__name__)
NEW_BUREAU = "feat_cif_bureau_salary_monthly_b24_new"
EVIDENCE_AED = 1000  # a window month the A1 engine counts as salary evidence


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


def _bureau_lines(
    old: DataFrame, new: DataFrame, cifs: DataFrame, since: Column
) -> list[str]:
    """Old vs new bureau rows of ``cifs`` from ``since`` on."""

    def scoped(df: DataFrame, side: str) -> DataFrame:
        return (
            df.join(cifs, "cif_id")
            .filter(F.col("month_end") >= since)
            .select("cif_id", "month_end", F.col("bureau_salary").alias(side))
        )

    a, b = scoped(old, "old"), scoped(new, "new")
    both = a.join(b, ["cif_id", "month_end"], "full")
    apart = F.abs(F.col("old") - F.col("new")) > 0.01 * F.greatest(
        F.abs("old"), F.abs("new")
    )
    s = both.agg(
        F.count("old").alias("old"),
        F.count("new").alias("new"),
        F.sum((F.col("old") == 0).cast("int")).alias("old_zero"),
        F.sum((F.col("new") == 0).cast("int")).alias("new_zero"),
        F.sum((F.col("new").isNull()).cast("int")).alias("only_old"),
        F.sum((F.col("old").isNull()).cast("int")).alias("only_new"),
        F.sum(apart.cast("int")).alias("apart"),
    ).collect()[0]
    n_new = max(s["new"], 1)
    return [
        f"  CIF-months: old {s['old']} (zero {s['old_zero']}) | new {s['new']} "
        f"(zero {s['new_zero']})",
        f"  only old {s['only_old']} | only new {s['only_new']} | in both, > 1% apart "
        f"{s['apart']}",
        "  new by salary_source:",
    ] + _counts(
        new.join(cifs, "cif_id").filter(F.col("month_end") >= since),
        ["salary_source"],
        n_new,
    )


def compare(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    old_bureau: DataFrame,
    new_bureau: DataFrame,
    old_income: DataFrame,
    new_income: DataFrame,
    old: DataFrame,
    new: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """Logs the B24 BUREAU / INCOME / A1 OUTPUT / A1 MOVES blocks for ``model_id``."""
    head = [f"  model_id {model_id}, latest month {persona_end_date}"]
    w = window_months(model_id)
    old_l = _latest(old, persona_end_date)
    new_l = _latest(new, persona_end_date).cache()
    n = new_l.count()
    cifs = (
        _latest(obs_base, persona_end_date)
        .filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
    )
    since = F.trunc(F.add_months(F.lit(str(persona_end_date)), -2 * w), "month")
    _block("B24 BUREAU", head + _bureau_lines(old_bureau, new_bureau, cifs, since))

    def evidence(df: DataFrame, side: str) -> DataFrame:
        return _latest(df, persona_end_date).select(
            *GRAIN,
            (F.coalesce(F.col("bureau_salary_w"), F.lit(0.0)) >= EVIDENCE_AED)
            .cast("int")
            .alias(f"{side}_bureau_evidence"),
        )

    states = old_l.select(
        *GRAIN,
        F.col("a1_state").alias("old_state"),
        F.col("a1_income_source").alias("old_source"),
        F.col("a1_income_level").alias("old_income"),
    ).join(
        new_l.select(
            *GRAIN,
            F.col("a1_state").alias("new_state"),
            F.col("a1_income_source").alias("new_source"),
            F.col("a1_income_level").alias("new_income"),
        ),
        list(GRAIN),
        "full",
    )
    income = evidence(old_income, "old").join(
        evidence(new_income, "new"), list(GRAIN), "full"
    )
    _block(
        "B24 INCOME",
        head
        + ["  bureau evidence in W (>= AED 1,000), old | new:"]
        + _counts(income, ["old_bureau_evidence", "new_bureau_evidence"], n)
        + ["  income source, old | new:"]
        + _counts(states, ["old_source", "new_source"], n)
        + ["  income level, old | new:"]
        + _counts(states, ["old_income", "new_income"], n),
    )
    _block(
        "B24 A1 OUTPUT",
        head
        + [f"  rows: new {n}", "  new state:"]
        + _counts(states, ["new_state"], n)
        + ["  old state:"]
        + _counts(states, ["old_state"], n),
    )
    _block(
        "B24 A1 MOVES",
        head + ["  old | new"] + _counts(states, ["old_state", "new_state"], n),
    )
    new_l.unpersist()


def create_b24_check_pipeline(product: str) -> Pipeline:
    """The new bureau feature, income signals and A1 state into temporary datasets, then
    the comparison."""
    prefix = f"crx_{product}_a1"
    obs = f"crx_{product}_obs_base"
    return Pipeline(
        [
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={"unified": "feat_bureau_salary_unified"},
                outputs=NEW_BUREAU,
                name=f"build_{prefix}_b24_bureau",
                tags=TAGS,
            ),
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": obs,
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": NEW_BUREAU,
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_income_b24_new",
                name=f"build_{prefix}_income_b24_new",
                tags=TAGS,
            ),
            node(
                func=build_a1_ability,
                inputs={
                    "obs_base": obs,
                    "income": f"{prefix}_income_b24_new",
                    "casa": f"{prefix}_casa_signals",
                    "cross_product": f"{prefix}_cross_product_signals",
                    "distress": f"{prefix}_distress_signals",
                    "eosb": f"{prefix}_eosb_signals",
                    "anchor": f"{prefix}_liquidity_anchor",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=f"{prefix}_b24_new",
                name=f"build_{prefix}_b24_new",
                tags=TAGS,
            ),
            node(
                func=compare,
                inputs={
                    "obs_base": obs,
                    "old_bureau": "feat_cif_bureau_salary_monthly",
                    "new_bureau": NEW_BUREAU,
                    "old_income": f"{prefix}_income_signals",
                    "new_income": f"{prefix}_income_b24_new",
                    "old": f"{prefix}_ability",
                    "new": f"{prefix}_b24_new",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name=f"compare_{prefix}_b24",
                tags=TAGS,
            ),
        ]
    )
