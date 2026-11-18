"""TEMPORARY (bundle 28): the A1 and A3 states before and after the bundle's step 8.

``crx_<p>_b28_snapshot`` (run before step 8) copies the persisted A1 and A3 state
columns into ``crx_<p>_b28_old_states`` (explicit entries in
``catalog_tmp_b28_check.yml``). ``crx_<p>_b28_compare`` (run after step 8) joins that
copy to the new persisted outputs and logs, for ``model_id``:

- ``B28 ROWS``: rows old / new / in both, and per month the rows whose A1 or A3 state
  changed;
- ``B28 A1``: latest persona month, ``a1_state`` old x new, and the
  ``a1_cross_product_level`` changes (F4: card parent link, point-in-time CIF);
- ``B28 A3``: latest persona month, ``a3_state`` and ``a3_commitments_level`` old x new
  (same-day payments, no Broken level).

The old tables predate bundle 25's rules as well (its step 8 is folded into this one).
Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b28_snapshot      (before step 8)
    kedro run --pipeline=crx_<p>_b28_compare       (after step 8)
"""

import logging

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from ._common import GRAIN

logger = logging.getLogger(__name__)
TAGS = ["crx_persona", "crx", "b28_check"]
A1_COLUMNS = ["a1_state", "a1_cross_product_level"]
A3_COLUMNS = ["a3_state", "a3_commitments_level"]


def snapshot(a1: DataFrame, a3: DataFrame) -> DataFrame:
    """``GRAIN`` and the A1 / A3 state columns (those the table has), one row per key."""

    def pick(df: DataFrame, cols: list[str]) -> DataFrame:
        return df.select(*GRAIN, *(c for c in cols if c in df.columns))

    return pick(a1, A1_COLUMNS).join(pick(a3, A3_COLUMNS), list(GRAIN), "full")


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _crosstab(df: DataFrame, col: str, changed_only: bool = False) -> list[str]:
    """``old_<col>`` x ``new_<col>`` counts over the rows with a value on either side
    (only the changed pairs if asked)."""
    old, new = f"old_{col}", f"new_{col}"
    if old not in df.columns or new not in df.columns:
        return [f"  {col}: not in both tables"]
    df = df.filter(F.col(old).isNotNull() | F.col(new).isNotNull())
    if changed_only:
        df = df.filter(~F.col(old).eqNullSafe(F.col(new)))
    total = max(df.count(), 1)
    rows = df.groupBy(old, new).count().orderBy(old, new).collect()
    return [f"  {col} old | new{' (changed only)' if changed_only else ''}:"] + (
        [
            f"    {r[old]} | {r[new]}: {r['count']} ({100 * r['count'] / total:.1f}%)"
            for r in rows
        ]
        or ["    none"]
    )


def _changed(col: str, columns: list[str]):
    """1 where a row on both sides changed ``col``."""
    old, new = f"old_{col}", f"new_{col}"
    if old not in columns or new not in columns:
        return F.lit(None).cast("int")
    both = F.col("old_row").isNotNull() & F.col("new_row").isNotNull()
    return (both & ~F.col(old).eqNullSafe(F.col(new))).cast("int")


def compare(  # pylint: disable=too-many-arguments
    old: DataFrame,
    a1: DataFrame,
    a3: DataFrame,
    *,
    model_id: str,
    persona_end_date: str,
) -> None:
    """Log the ``B28`` blocks (module docstring)."""
    new = snapshot(a1, a3)

    def side(df: DataFrame, prefix: str) -> DataFrame:
        return df.select(
            *GRAIN,
            F.lit(1).alias(f"{prefix}_row"),
            *(F.col(c).alias(f"{prefix}_{c}") for c in df.columns if c not in GRAIN),
        )

    pairs = (
        side(old, "old").join(side(new, "new"), list(GRAIN), "full").localCheckpoint()
    )
    month = F.last_day("observation_date").alias("month")
    per_month = (
        pairs.groupBy(month)
        .agg(
            F.sum("old_row").alias("old"),
            F.sum("new_row").alias("new"),
            F.sum(F.col("old_row") * F.col("new_row")).alias("both"),
            F.sum(_changed("a1_state", pairs.columns)).alias("a1_changed"),
            F.sum(_changed("a3_state", pairs.columns)).alias("a3_changed"),
        )
        .orderBy("month")
        .collect()
    )
    _block(
        "B28 ROWS",
        model_id,
        ["  month: rows old / new / both, a1_state / a3_state changed (rows in both)"]
        + [
            f"    {r['month']}: {r['old']} / {r['new']} / {r['both']},"
            f" {r['a1_changed']}, {r['a3_changed']}"
            for r in per_month
        ],
    )
    latest = pairs.filter(
        F.trunc("observation_date", "month")
        == F.trunc(F.lit(str(persona_end_date)), "month")
    )
    _block(
        "B28 A1",
        model_id,
        _crosstab(latest, "a1_state")
        + _crosstab(latest, "a1_cross_product_level", changed_only=True),
    )
    _block(
        "B28 A3",
        model_id,
        _crosstab(latest, "a3_state") + _crosstab(latest, "a3_commitments_level"),
    )


def create_snapshot_pipeline(product: str) -> Pipeline:
    """Copy the persisted A1 / A3 states of ``product`` before step 8."""
    return pipeline(
        [
            node(
                func=snapshot,
                inputs={
                    "a1": f"crx_{product}_a1_ability",
                    "a3": f"crx_{product}_a3_payment_credibility",
                },
                outputs=f"crx_{product}_b28_old_states",
                name=f"crx_{product}_b28_snapshot",
                tags=TAGS,
            )
        ]
    )


def create_compare_pipeline(product: str) -> Pipeline:
    """Log the old x new states of ``product`` after step 8."""
    return pipeline(
        [
            node(
                func=compare,
                inputs={
                    "old": f"crx_{product}_b28_old_states",
                    "a1": f"crx_{product}_a1_ability",
                    "a3": f"crx_{product}_a3_payment_credibility",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name=f"crx_{product}_b28_compare",
                tags=TAGS,
            )
        ]
    )
