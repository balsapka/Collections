"""TEMPORARY (bundle 31): the UC1 stated block before and after the bundle's step 8.

``crx_<p>_b31_snapshot`` (run before step 8) copies the persisted UC1 block's evidence and
states into ``crx_<p>_b31_old_uc1`` (explicit entry in ``catalog_tmp_b31_check.yml``).
``crx_<p>_b31_compare`` (run after step 8) logs, for ``model_id``:

- ``B31 ROWS``: per month, rows and rows with a UC1 value;
- ``B31 DIST``: at the UC1 month, ``uc1_evidence``, the states, UC1's confidence, the
  flags, and ``uc1_evidence`` by A2 reachability;
- ``B31 OLD NEW``: per account, the old block (persona end month) x the new one (UC1
  month): evidence, A5, A6;
- ``B31 PAID``: at the UC1 month, paid_due / paid_any over the next month (payments
  reaching max(the due at the month end, 100 AED) / 100 AED, from the A3 dues and
  payments) by state and flag, inside the A1 / A3 states, with two AUCs.

Counts under 10 show as "<10". Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b31_snapshot      (before step 8)
    kedro run --pipeline=crx_<p>_b31_compare       (after step 8)
"""

import logging

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from ._common import GRAIN
from .uc1_stated.signals import scored_month

logger = logging.getLogger(__name__)
TAGS = ["crx_persona", "crx", "b31_check"]
OLD_COLUMNS = ["uc1_evidence", "a5_state", "a6_state"]
MIN_CELL = 10
A5_ORDER = {"able": 3, "partly_able": 2, "not_stated": 1, "unable": 0}
A6_ORDER = {"pays_in_full": 3, "partly_or_later": 2, "not_stated": 1, "refuses": 0}


def snapshot(uc1: DataFrame) -> DataFrame:
    """``GRAIN`` and the old block's evidence and states (those the table has)."""
    return uc1.select(*GRAIN, *(c for c in OLD_COLUMNS if c in uc1.columns))


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _n(count: int) -> str:
    return f"<{MIN_CELL}" if count < MIN_CELL else str(count)


def _counts(df: DataFrame, cols: list[str], title: str) -> list[str]:
    total = max(df.count(), 1)
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [f"  {title}:"] + [
        f"    {' | '.join(str(r[c]) for c in cols)}: {_n(r['count'])}"
        f" ({100 * r['count'] / total:.1f}%)"
        for r in rows
    ]


def _rates(df: DataFrame, cols: list[str], title: str) -> list[str]:
    """n, paid_due % and paid_any % per value of ``cols``."""
    rows = (
        df.groupBy(*cols)
        .agg(
            F.count(F.lit(1)).alias("n"),
            F.avg("paid_due").alias("due"),
            F.avg("paid_any").alias("any"),
        )
        .orderBy(*cols)
        .collect()
    )
    out = [f"  {title} (n, paid_due %, paid_any %):"]
    for r in rows:
        key = " | ".join(str(r[c]) for c in cols)
        if r["n"] < MIN_CELL:
            out.append(f"    {key}: <{MIN_CELL}")
        else:
            out.append(
                f"    {key}: {r['n']}, {100 * r['due']:.1f}, {100 * r['any']:.1f}"
            )
    return out


def _auc(df: DataFrame, col: str, order: dict[str, int], title: str) -> list[str]:
    """AUC of ``order`` on paid_due over the rows whose ``col`` is in it (ties = 1/2)."""
    score = F.create_map(*[F.lit(x) for kv in order.items() for x in kv])[F.col(col)]
    cells = (
        df.select(score.alias("s"), "paid_due")
        .filter(F.col("s").isNotNull())
        .groupBy("s")
        .agg(F.sum("paid_due").alias("pos"), F.count(F.lit(1)).alias("n"))
        .collect()
    )
    pos = {r["s"]: r["pos"] for r in cells}
    neg = {r["s"]: r["n"] - r["pos"] for r in cells}
    n_pos, n_neg = sum(pos.values()), sum(neg.values())
    if not n_pos or not n_neg:
        return [f"  {title}: no AUC (one outcome only)"]
    won = sum(
        pos[a] * neg[b] * (1.0 if a > b else 0.5 if a == b else 0.0)
        for a in pos
        for b in neg
    )
    return [f"  {title}: {won / (n_pos * n_neg):.3f} (n {n_pos + n_neg})"]


def _outcomes(base: DataFrame, dues: DataFrame, payments: DataFrame) -> DataFrame:
    """``GRAIN`` + paid_due / paid_any over the month after the observation date."""
    obs = F.col("observation_date")
    latest_due = (
        base.select(*GRAIN)
        .join(dues.select("account_id", "cycle_start", "due_amount"), "account_id")
        .filter(F.col("cycle_start") <= obs)
        .withColumn(
            "_r",
            F.row_number().over(
                Window.partitionBy(*GRAIN).orderBy(F.col("cycle_start").desc())
            ),
        )
        .filter("_r = 1")
        .select(*GRAIN, "due_amount")
    )
    paid = (
        base.select(*GRAIN)
        .join(payments.select("account_id", "pay_date", "amount"), "account_id")
        .filter((F.col("pay_date") > obs) & (F.col("pay_date") <= F.add_months(obs, 1)))
        .groupBy(*GRAIN)
        .agg(F.sum("amount").alias("_paid"))
    )
    amount = F.coalesce(F.col("_paid"), F.lit(0))
    due = F.greatest(F.coalesce(F.col("due_amount"), F.lit(0)), F.lit(100))
    return (
        base.select(*GRAIN)
        .join(latest_due, list(GRAIN), "left")
        .join(paid, list(GRAIN), "left")
        .select(
            *GRAIN,
            (amount >= due).cast("int").alias("paid_due"),
            (amount >= 100).cast("int").alias("paid_any"),
        )
    )


def _promise_kind() -> Column:
    a6 = F.col("a6_state")
    named = (F.col("a6_amount_named_flag") == 1) | (F.col("a6_date_named_flag") == 1)
    paying = a6.isin("pays_in_full", "partly_or_later")
    flag = F.col("stated_promise_unlogged_flag")
    return (
        F.when(F.col("uc1_evidence") != "extracted", "no_uc1")
        .when(flag == 1, "said_unlogged")
        .when(paying & named & (flag == 0), "said_logged")
        .when(paying & named, "said_no_dated_call")
        .when(paying, "paying_no_amount_date")
        .otherwise("other_reading")
    )


def compare(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    old: DataFrame,
    uc1: DataFrame,
    a1: DataFrame,
    a2: DataFrame,
    a3: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    *,
    model_id: str,
    persona_end_date: str,
    uc1_month_end: str | None,
) -> None:
    """Log the ``B31`` blocks (module docstring)."""
    month = scored_month(persona_end_date, uc1_month_end)
    per_month = (
        uc1.groupBy(F.last_day("observation_date").alias("month"))
        .agg(
            F.count(F.lit(1)).alias("rows"),
            F.count("uc1_evidence").alias("scored"),
        )
        .orderBy("month")
        .collect()
    )
    _block(
        "B31 ROWS",
        model_id,
        ["  month: rows / with a UC1 value"]
        + [f"    {r['month']}: {r['rows']} / {r['scored']}" for r in per_month],
    )

    def at(df: DataFrame, date: str) -> DataFrame:
        return df.filter(
            F.trunc("observation_date", "month") == F.trunc(F.lit(str(date)), "month")
        )

    new = (
        at(uc1, month)
        .join(at(a1, month).select(*GRAIN, "a1_state"), list(GRAIN), "left")
        .join(at(a2, month).select(*GRAIN, "reachability_state"), list(GRAIN), "left")
        .join(
            at(a3, month).select(*GRAIN, "a3_state", "a3_commitments_level"),
            list(GRAIN),
            "left",
        )
        .localCheckpoint()
    )
    stated = new.filter(F.col("uc1_evidence") == "extracted")
    dist = []
    for col in ("uc1_evidence", "a5_state", "a6_state"):
        dist += _counts(new, [col], col)
    for col in (
        "a5_confidence",
        "a6_confidence",
        "stated_promise_unlogged_flag",
        "verify_stated_ability_flag",
        "stated_dispute",
        "stated_request_flag",
    ):
        dist += _counts(stated, [col], f"{col} (UC1 rows)")
    dist += _counts(new, ["reachability_state", "uc1_evidence"], "reach x evidence")
    _block("B31 DIST", model_id, [f"  UC1 month {month}"] + dist)

    def side(df: DataFrame, prefix: str) -> DataFrame:
        return df.select(
            "account_id", *(F.col(c).alias(f"{prefix}_{c}") for c in OLD_COLUMNS)
        )

    pairs = side(at(old, persona_end_date), "old").join(
        side(new, "new"), "account_id", "full"
    )
    old_new = [f"  old = {persona_end_date} month, new = {month} month, per account"]
    for col in OLD_COLUMNS:
        old_new += _counts(pairs, [f"old_{col}", f"new_{col}"], f"{col} old | new")
    _block("B31 OLD NEW", model_id, old_new)

    rows = (
        new.join(_outcomes(new, dues, payments), list(GRAIN), "left")
        .withColumn("promise_kind", _promise_kind())
        .localCheckpoint()
    )
    rows_stated = rows.filter(F.col("uc1_evidence") == "extracted")
    unknown = rows_stated.filter(F.col("a1_state") == "unknown")
    no_promise = rows_stated.filter(F.col("a3_commitments_level") == "no_promise")
    paid = (
        [f"  UC1 month {month}; outcome = the next month"]
        + _rates(rows, ["uc1_evidence"], "evidence")
        + _rates(rows, ["a1_state", "a5_state"], "A1 x A5")
        + _auc(unknown, "a5_state", A5_ORDER, "AUC A5 inside A1 unknown")
        + _rates(rows, ["a3_commitments_level", "a6_state"], "A3 level x A6")
        + _auc(no_promise, "a6_state", A6_ORDER, "AUC A6 inside A3 no_promise")
        + _rates(rows, ["a3_state", "a6_state"], "A3 state x A6")
        + _rates(rows_stated, ["a5_reason"], "reason (UC1 rows)")
        + _rates(unknown, ["a5_reason"], "reason inside A1 unknown")
        + _rates(
            rows_stated.filter(F.col("a1_state") == "low"),
            ["verify_stated_ability_flag"],
            "verify flag inside A1 low",
        )
        + _rates(rows, ["a3_commitments_level", "promise_kind"], "A3 level x promise")
        + _rates(rows, ["promise_kind"], "promise")
        + _rates(
            rows_stated.withColumn(
                "dispute_any", (F.col("stated_dispute") != "none").cast("int")
            ),
            ["dispute_any"],
            "stated dispute (UC1 rows)",
        )
        + _rates(rows_stated, ["stated_request_flag"], "request (UC1 rows)")
        + _rates(rows_stated, ["a6_confidence", "a6_state"], "A6 by confidence")
    )
    _block("B31 PAID", model_id, paid)


def create_snapshot_pipeline(product: str) -> Pipeline:
    """Copy the persisted UC1 block of ``product`` before step 8."""
    return pipeline(
        [
            node(
                func=snapshot,
                inputs={"uc1": f"crx_{product}_uc1_stated"},
                outputs=f"crx_{product}_b31_old_uc1",
                name=f"crx_{product}_b31_snapshot",
                tags=TAGS,
            )
        ]
    )


def create_compare_pipeline(product: str) -> Pipeline:
    """Log the ``B31`` blocks of ``product`` after step 8."""
    return pipeline(
        [
            node(
                func=compare,
                inputs={
                    "old": f"crx_{product}_b31_old_uc1",
                    "uc1": f"crx_{product}_uc1_stated",
                    "a1": f"crx_{product}_a1_ability",
                    "a2": f"crx_{product}_a2_locatability",
                    "a3": f"crx_{product}_a3_payment_credibility",
                    "dues": f"crx_{product}_a3_dues",
                    "payments": f"crx_{product}_a3_payments",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                    "uc1_month_end": "params:uc1_month_end",
                },
                outputs=None,
                name=f"crx_{product}_b31_compare",
                tags=TAGS,
            )
        ]
    )
