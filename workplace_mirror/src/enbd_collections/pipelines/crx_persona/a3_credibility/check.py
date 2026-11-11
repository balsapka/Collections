"""TEMPORARY (A3 bundle 23): the effect of the bundle on the latest month.

The A3 engine runs twice on persona_end_date's month: ``new`` as shipped
(``PROMISE_DEADLINE``) and ``old`` with bundle 20's deadline (CC the next statement, RL
the end of the next month). ``b20`` is the persisted A3 output (bundle 20). b20 -> old is
the Unknown rule (D-A3-27), old -> new the deadline (D-A3-28; at 60-180 loans only).
Logs ``A3 OUTPUT``, ``A3 PROMISES``, ``A3 LEVELS``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a3_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .classify import build_a3_credibility
from .pipeline import TAGS, create_a3_pipeline
from .signals import build_commitment_signals
from .sources import build_promise_events

logger = logging.getLogger(__name__)
NS = "a3_check"
OLD_DEADLINE = {"cc": "next_statement", "rl": "next_month_end"}  # bundle 20


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def latest_month(obs_base: DataFrame, persona_end_date: str) -> DataFrame:
    """The base rows of persona_end_date's month."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], total: int) -> list[str]:
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "  "
        + " | ".join(str(r[c]) for c in cols)
        + f": {r['count']} ({100 * r['count'] / max(total, 1):.1f}%)"
        for r in rows
    ]


def compare_a3(
    new: DataFrame,
    old: DataFrame,
    events_new: DataFrame,
    events_old: DataFrame,
    b20: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """The check blocks. The event tables are checkpointed first: they are in memory,
    and every count would otherwise rebuild them."""
    events_new, events_old = (df.localCheckpoint() for df in (events_new, events_old))
    short = "^payment_credibility_"
    both = (
        new.select(
            "account_id",
            "observation_date",
            "commitments_window_start",
            F.regexp_replace("a3_state", short, "").alias("new"),
            F.col("a3_commitments_level").alias("new_level"),
            F.col("commitments_concluded").alias("new_concluded"),
            F.col("commitments_kept").alias("new_kept"),
        )
        .join(
            old.select(
                "account_id",
                F.regexp_replace("a3_state", short, "").alias("old"),
                F.col("a3_commitments_level").alias("old_level"),
                F.col("commitments_concluded").alias("old_concluded"),
                F.col("commitments_kept").alias("old_kept"),
            ),
            "account_id",
        )
        .join(
            b20.where(
                F.trunc("observation_date", "month")
                == F.trunc(F.lit(str(persona_end_date)), "month")
            ).select(
                "account_id", F.regexp_replace("a3_state", short, "").alias("b20")
            ),
            "account_id",
            "left",
        )
        .localCheckpoint()
    )
    n = both.count()
    head = [f"model_id: {model_id}", f"rows: {n}"]

    lines = list(head)
    for col in ("b20", "old", "new"):
        lines += [f"state {col}:"] + _counts(both, [col], n)
    for a, b, what in (
        ("b20", "new", "whole bundle"),
        ("b20", "old", "Unknown rule"),
        ("old", "new", "deadline"),
    ):
        moved = both.where(~F.col(a).eqNullSafe(F.col(b))).count()
        lines += [
            f"{a} x {b} ({what}), changed {moved} ({100 * moved / max(n, 1):.1f}%):"
        ]
        lines += _counts(both, [a, b], n)
    _block("A3 OUTPUT", lines)

    win = both.select("account_id", "observation_date", "commitments_window_start")
    keys = ["account_id", "event_date"]
    e = (
        events_old.select(
            *keys,
            "event_kind",
            F.col("promise_cutoff").alias("cutoff_old"),
            F.col("promise_outcome").alias("outcome_old"),
        )
        .join(
            events_new.select(
                *keys,
                F.col("promise_cutoff").alias("cutoff_new"),
                F.col("promise_outcome").alias("outcome_new"),
            ),
            keys,
        )
        .join(win, "account_id")
        .where(
            (F.col("event_date") >= F.col("commitments_window_start"))
            & (F.col("event_date") <= F.col("observation_date"))
        )
        .localCheckpoint()
    )
    m = e.count()
    lines = head + [f"events in the window: {m}"]
    for tag in ("old", "new"):
        done = e.where(F.col(f"cutoff_{tag}") <= F.col("observation_date"))
        c = done.count()
        lines += [f"{tag}: concluded {c}, outcome:"]
        lines += _counts(done, [f"outcome_{tag}"], c)
    both_done = e.where(
        (F.col("cutoff_old") <= F.col("observation_date"))
        & (F.col("cutoff_new") <= F.col("observation_date"))
    )
    c = both_done.count()
    lines += [f"concluded under both: {c}, outcome old x new:"]
    lines += _counts(both_done, ["outcome_old", "outcome_new"], c)
    changed = both_done.where(F.col("outcome_old") != F.col("outcome_new"))
    k = changed.count()
    day = F.dayofmonth("event_date")
    lines += [f"changed outcome: {k}, by event kind:"]
    lines += _counts(changed, ["event_kind"], k)
    lines += ["changed outcome by promise day of month:"]
    lines += _counts(
        changed.withColumn(
            "promise_day",
            F.when(day <= 10, "01-10").when(day <= 20, "11-20").otherwise("21-31"),
        ),
        ["promise_day"],
        k,
    )
    lines += ["all concluded-under-both events by promise day of month:"]
    lines += _counts(
        both_done.withColumn(
            "promise_day",
            F.when(day <= 10, "01-10").when(day <= 20, "11-20").otherwise("21-31"),
        ),
        ["promise_day"],
        c,
    )
    accounts = {
        c: both.where(F.col(c) > 0).count()
        for c in ("old_concluded", "new_concluded", "old_kept", "new_kept")
    }
    lines.append(
        f"accounts with >= 1 concluded promise: old {accounts['old_concluded']}, "
        f"new {accounts['new_concluded']}; with >= 1 kept: old {accounts['old_kept']}, "
        f"new {accounts['new_kept']}"
    )
    _block("A3 PROMISES", lines)

    lines = list(head)
    for col in ("old_level", "new_level"):
        lines += [f"{col}:"] + _counts(both, [col], n)
    lines += ["old_level x new_level:"] + _counts(both, ["old_level", "new_level"], n)
    _block("A3 LEVELS", lines)


def create_a3_check_pipeline(product: str, dues, payments) -> Pipeline:
    """The latest month through the A3 engine in the ``a3_check`` namespace (nothing real
    is overwritten): as shipped and with bundle 20's deadline; then the blocks."""
    p = f"crx_{product}_a3"
    obs = f"crx_{product}_obs_base"
    final = f"{p}_check_new"
    base = create_a3_pipeline(product, final, dues, payments)

    def ns(
        name: str,
    ) -> str:  # a check-only dataset name (no dots: Kedro reserves them)
        return f"{NS}__{name}"

    inputs = {i for i in base.inputs() if not i.startswith("params:")} - {obs}
    params = {i for i in base.all_inputs() if i.startswith("params:")}
    # Every intermediate gets an explicit check name, so the namespace only prefixes
    # the node names.
    scoped = pipeline(
        base,
        namespace=NS,
        inputs={**{i: i for i in inputs}, obs: ns("obs_latest")},
        outputs={o: o if o == final else ns(o) for o in base.all_outputs()},
        parameters=params,
    )
    old = OLD_DEADLINE[product]
    extra = [
        node(
            func=latest_month,
            inputs={
                "obs_base": obs,
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=ns("obs_latest"),
            name=f"{p}_check_latest",
            tags=TAGS,
        ),
        node(
            func=partial(build_promise_events, product=product, deadline=old),
            inputs={
                "obs_base": ns("obs_latest"),
                "followup": "dcore_prm_followup_outcomes",
                "agreements": "prm_dcore_account_agreements",
                "instalments": ns(f"{p}_instalments"),
                "dues": ns(f"{p}_dues"),
                "payments": ns(f"{p}_payments"),
                "model_id": "params:model_id",
            },
            outputs=ns("promise_events_old"),
            name=f"{p}_check_events_old",
            tags=TAGS,
        ),
        node(
            func=build_commitment_signals,
            inputs={"episode": ns(f"{p}_episode"), "events": ns("promise_events_old")},
            outputs=ns("commitments_old"),
            name=f"{p}_check_commitments_old",
            tags=TAGS,
        ),
        node(
            func=partial(build_a3_credibility, product=product, deadline=old),
            inputs={
                "episode": ns(f"{p}_episode"),
                "commitments": ns("commitments_old"),
                "dlq_payments": ns(
                    f"{p}_dlq_payment_signals_single_payment_cycle_count"
                ),
                "pre_dlq": ns(
                    f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
                ),
                "contacts": ns(f"{p}_strong_negative_signals"),
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=f"{p}_check_old",
            name=f"{p}_check_state_old",
            tags=TAGS,
        ),
        node(
            func=compare_a3,
            inputs={
                "new": final,
                "old": f"{p}_check_old",
                "events_new": ns(f"{p}_promise_events"),
                "events_old": ns("promise_events_old"),
                "b20": f"{p}_payment_credibility",
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=None,
            name=f"{p}_check_compare",
            tags=TAGS,
        ),
    ]
    return scoped + Pipeline(extra)
