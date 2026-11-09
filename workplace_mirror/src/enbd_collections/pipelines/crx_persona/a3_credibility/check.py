"""TEMPORARY (A3 bundle 20): the new A3 on the latest month, with promise events judged
by GRR's deadline and by 30 days, against the A3 output persisted before the bundle
(bundle 17: instalments, Moderate from 1). Logs ``A3 OUTPUT``, ``A3 PROMISES``,
``A3 LEVELS``, ``A3 CONTACTS``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a3_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .classify import build_a3_credibility
from .constants import HIGH_FROM, MODERATE_FROM
from .pipeline import TAGS, create_a3_pipeline
from .signals import build_commitment_signals
from .sources import build_promise_events

logger = logging.getLogger(__name__)
NS = "a3_check"
DEADLINE_30D = {"cc": "30_days", "rl": "30_days_month_end"}


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


def _rung(points: Column, refusal: Column, state: Column) -> Column:
    """The A3 state from points with today's cut-offs (old rows, Moderate from 2)."""
    rung = F.when(points >= HIGH_FROM, 2).when(points >= MODERATE_FROM, 1).otherwise(0)
    rung = F.greatest(rung - F.coalesce(refusal, F.lit(False)).cast("int"), F.lit(0))
    label = F.element_at(F.array(*map(F.lit, ("low", "moderate", "high"))), rung + 1)
    return F.when(state == "payment_credibility_unknown", "unknown").otherwise(label)


def _short(state: Column) -> Column:
    return F.regexp_replace(state, "^payment_credibility_", "")


def compare_a3(
    old: DataFrame,
    grr: DataFrame,
    d30: DataFrame,
    events_grr: DataFrame,
    events_30d: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """The check blocks (latest month). The inputs are checkpointed first: the event
    tables are in memory, and every count would otherwise rebuild them."""
    grr, d30, events_grr, events_30d = (
        df.localCheckpoint() for df in (grr, d30, events_grr, events_30d)
    )
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    newest = F.row_number().over(
        Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    )
    o = (
        old.filter(F.trunc("observation_date", "month") == month)
        .withColumn("_r", newest)
        .where("_r = 1")
        .select(
            "account_id",
            _short(F.col("a3_state")).alias("old"),
            _rung(
                F.col("a3_points_total"), F.col("a3_refusal_flag"), F.col("a3_state")
            ).alias("old_m2"),
            F.col("a3_commitments_level").alias("old_level"),
            F.col("commitments_concluded").alias("old_concluded"),
            F.col("last_rpc_disposition").alias("old_disp"),
            F.col("a3_refusal_flag").alias("old_refusal"),
        )
    )
    g = grr.select(
        "account_id",
        "observation_date",
        "commitments_window_start",
        _short(F.col("a3_state")).alias("grr"),
        F.col("a3_commitments_level").alias("grr_level"),
        F.col("commitments_concluded").alias("grr_concluded"),
        F.col("last_rpc_disposition").alias("new_disp"),
        F.col("a3_refusal_flag").alias("new_refusal"),
    )
    f = d30.select(
        "account_id",
        _short(F.col("a3_state")).alias("d30"),
        F.col("a3_commitments_level").alias("d30_level"),
        F.col("commitments_concluded").alias("d30_concluded"),
    )
    both = g.join(f, "account_id").join(o, "account_id", "left").localCheckpoint()
    n = both.count()
    head = [f"model_id: {model_id}", f"rows new: {n}, old matched: {o.count()}"]

    lines = list(head)
    for col in ("old", "old_m2", "grr", "d30"):
        lines += [f"state {col}:"] + _counts(both, [col], n)
    lines += ["old (Moderate from 2) x new (GRR):"]
    lines += _counts(both, ["old_m2", "grr"], n)
    lines += ["new GRR x new 30 days:"] + _counts(both, ["grr", "d30"], n)
    _block("A3 OUTPUT", lines)

    win = g.select("account_id", "observation_date", "commitments_window_start")
    lines = list(head)
    for name, ev in (("GRR", events_grr), ("30 days", events_30d)):
        e = (
            ev.join(win, "account_id")
            .where(
                (F.col("event_date") >= F.col("commitments_window_start"))
                & (F.col("event_date") <= F.col("observation_date"))
            )
            .localCheckpoint()
        )
        concluded = e.where(F.col("promise_cutoff") <= F.col("observation_date"))
        m = e.count()
        lines += [f"[{name}] events in the window: {m}, by kind | source:"]
        lines += _counts(e, ["event_kind", "event_source"], m)
        c = concluded.count()
        lines += [f"[{name}] concluded: {c}, outcome by kind:"]
        lines += _counts(concluded, ["event_kind", "promise_outcome"], c)
        if name == "GRR":
            lines += ["[GRR] follow-up names (events in the window):"]
            lines += _counts(
                e.where(F.col("event_name").isNotNull()), ["event_name"], m
            )
    lines += [
        "accounts with >= 1 concluded promise / instalment: "
        + ", ".join(
            f"{k} {both.where(F.col(c) > 0).count()}"
            for k, c in (
                ("old", "old_concluded"),
                ("GRR", "grr_concluded"),
                ("30 days", "d30_concluded"),
            )
        )
    ]
    _block("A3 PROMISES", lines)

    lines = list(head)
    for col in ("old_level", "grr_level", "d30_level"):
        lines += [f"{col}:"] + _counts(both, [col], n)
    lines += ["old level x GRR level:"] + _counts(both, ["old_level", "grr_level"], n)
    lines += ["GRR level x 30 days level:"]
    lines += _counts(both, ["grr_level", "d30_level"], n)
    _block("A3 LEVELS", lines)

    lines = head + ["refusal old x new:"]
    lines += _counts(both, ["old_refusal", "new_refusal"], n)
    lines += ["last right-party disposition old x new:"]
    lines += _counts(both, ["old_disp", "new_disp"], n)
    _block("A3 CONTACTS", lines)


def create_a3_check_pipeline(product: str, dues, payments) -> Pipeline:
    """The latest month through the A3 engine in the ``a3_check`` namespace (nothing real
    is overwritten): GRR's deadline (the shipped one) and 30 days, then the blocks."""
    p = f"crx_{product}_a3"
    obs = f"crx_{product}_obs_base"
    final = f"{p}_check_grr"
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
    d30 = DEADLINE_30D[product]
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
            func=partial(build_promise_events, deadline=d30),
            inputs={
                "obs_base": ns("obs_latest"),
                "followup": "dcore_prm_followup_outcomes",
                "agreements": "prm_dcore_account_agreements",
                "instalments": ns(f"{p}_instalments"),
                "dues": ns(f"{p}_dues"),
                "payments": ns(f"{p}_payments"),
            },
            outputs=ns("promise_events_30d"),
            name=f"{p}_check_events_30d",
            tags=TAGS,
        ),
        node(
            func=build_commitment_signals,
            inputs={
                "episode": ns(f"{p}_episode"),
                "events": ns("promise_events_30d"),
            },
            outputs=ns("commitments_30d"),
            name=f"{p}_check_commitments_30d",
            tags=TAGS,
        ),
        node(
            func=partial(build_a3_credibility, deadline=d30),
            inputs={
                "episode": ns(f"{p}_episode"),
                "commitments": ns("commitments_30d"),
                "dlq_payments": ns(
                    f"{p}_dlq_payment_signals_single_payment_cycle_count"
                ),
                "pre_dlq": ns(
                    f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
                ),
                "contacts": ns(f"{p}_strong_negative_signals"),
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=f"{p}_check_30d",
            name=f"{p}_check_state_30d",
            tags=TAGS,
        ),
        node(
            func=compare_a3,
            inputs={
                "old": f"{p}_payment_credibility",
                "grr": final,
                "d30": f"{p}_check_30d",
                "events_grr": ns(f"{p}_promise_events"),
                "events_30d": ns("promise_events_30d"),
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=None,
            name=f"{p}_check_compare",
            tags=TAGS,
        ),
    ]
    return scoped + Pipeline(extra)
