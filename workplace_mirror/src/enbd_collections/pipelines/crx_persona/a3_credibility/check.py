"""TEMPORARY (A3 bundle): the new A3 on the latest month, with both Dimension A judges,
against the A3 output persisted before the bundle. Logs ``A3 OUTPUT``, ``A3 COMMITMENTS``,
``A3 BROKEN``, ``A3 CONTACTS``, ``A3 EPISODE``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a3_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .classify import build_a3_credibility
from .pipeline import TAGS, create_a3_pipeline
from .signals import build_commitment_signals, build_contact_signals
from .constants import GRACE

logger = logging.getLogger(__name__)
NS = "a3_check"


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


def _state(
    points_a: Column,
    points_bc: Column,
    refusal: Column,
    override: Column,
    unknown: Column,
) -> Column:
    """The A3 ladder for a what-if of the Broken weight."""
    pts = points_a + points_bc
    demote = refusal | override
    rung = (
        F.when(pts >= 4, F.when(demote, "moderate").otherwise("high"))
        .when((pts >= 1) & ~demote, "moderate")
        .otherwise("low")
    )
    return F.when(unknown, "unknown").otherwise(rung)


def compare_a3(
    old: DataFrame,
    pay: DataFrame,
    dcore: DataFrame,
    uncapped: DataFrame,
    model_id: str,
    persona_end_date: str,
    floor: str | None,
) -> None:
    """The check blocks (latest month)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    old_m = old.filter(F.trunc("observation_date", "month") == month)
    keep = ["a3_state_v1", "a3_commitments_level", "a3_strong_negative_reason"]
    old_m = old_m.select(
        "account_id", "observation_date", *[c for c in keep if c in old_m.columns]
    )
    newest = F.row_number().over(
        Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    )
    old_m = (
        old_m.withColumn("_r", newest).where("_r = 1").drop("_r", "observation_date")
    )
    n = pay.count()
    p, d = pay.alias("p"), dcore.alias("d")
    both = p.join(d, "account_id").join(old_m.alias("o"), "account_id", "left")
    head = [
        f"model_id: {model_id}",
        f"rows new: {n}, old (latest per account): {old_m.count()}",
    ]

    lines = head + ["old a3_state_v1 x new (payments):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("p.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["old x new (dcore):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("d.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["new dcore x new payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_state").alias("dcore"), F.col("p.a3_state").alias("payments")
        ),
        ["dcore", "payments"],
        n,
    )
    _block("A3 OUTPUT", lines)

    lines = head + ["Dimension A level, dcore x payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_commitments_level").alias("dcore"),
            F.col("p.a3_commitments_level").alias("payments"),
        ),
        ["dcore", "payments"],
        n,
    )
    s = both.agg(
        *[
            F.sum(f"{j}.{c}").alias(f"{j}_{c}")
            for j in ("d", "p")
            for c in ("commitments_concluded", "commitments_kept")
        ]
    ).first()
    lines += [
        f"instalments concluded / kept: dcore {s['d_commitments_concluded']} / "
        f"{s['d_commitments_kept']}, payments {s['p_commitments_concluded']} / "
        f"{s['p_commitments_kept']}"
    ]
    if "a3_commitments_level" in old_m.columns:
        lines += ["old level x new (payments):"]
        lines += _counts(
            both.select(
                F.col("o.a3_commitments_level").alias("old"),
                F.col("p.a3_commitments_level").alias("new"),
            ),
            ["old", "new"],
            n,
        )
    _block("A3 COMMITMENTS", lines)

    lines = list(head)
    for j, frame in (("payments", pay), ("dcore", dcore)):
        lvl = F.col("a3_commitments_level")
        pa = F.when(lvl == "kept", 2).when(lvl == "partly_kept", 1).otherwise(0)
        bc = F.col("a3_dlq_payments_points") + F.col("a3_pre_dlq_record_points")
        broken = lvl == "broken"
        unknown = F.col("a3_state") == "payment_credibility_unknown"
        f = frame.select(
            broken.alias("broken"),
            bc.alias("bc"),
            _state(pa, bc, F.col("a3_refusal_flag"), broken, unknown).alias(
                "v0_override"
            ),
            _state(pa, bc, F.col("a3_refusal_flag"), F.lit(False), unknown).alias(
                "v1_zero"
            ),
            _state(
                pa - broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v2_minus1"),
            _state(
                pa - 2 * broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v3_minus2"),
        )
        lines += [f"[{j}] Broken rows by B + C points:"]
        lines += _counts(f.where("broken"), ["bc"], n)
        for v in ("v0_override", "v1_zero", "v2_minus1", "v3_minus2"):
            lines += [f"[{j}] state {v}:"] + _counts(f, [v], n)
    _block("A3 BROKEN", lines)

    u = uncapped.select("account_id", F.col("a3_refusal_flag").alias("uncapped"))
    c = pay.join(u, "account_id", "left")
    lines = head + [
        f"{col}: {c.where(F.col(col)).count()}"
        for col in (
            "a3_refusal_flag",
            "refusal_followed_by_plan",
            "refusal_followed_by_payment",
            "a3_dispute_flag",
            "a3_hung_up_last",
            "a3_no_pickup_after_contact",
        )
    ]
    lines += [
        f"refusal without the 24-month cap: {c.where(F.col('uncapped')).count()}",
        "last right-party disposition:",
    ]
    lines += _counts(pay, ["last_rpc_disposition"], n)
    if "a3_strong_negative_reason" in old_m.columns:
        lines += ["old strong negative x new refusal:"]
        lines += _counts(
            both.select(
                F.col("o.a3_strong_negative_reason").alias("old"),
                F.col("p.a3_refusal_flag").alias("refusal"),
            ),
            ["old", "refusal"],
            n,
        )
    _block("A3 CONTACTS", lines)

    lines = head + ["unknown reason:"] + _counts(pay, ["a3_unknown_reason"], n)
    lines += ["Dimension C reason x level:"]
    lines += _counts(pay, ["pre_dlq_reason", "a3_pre_dlq_payment_level"], n)
    if floor:
        cut = pay.where(
            (F.col("pre_dlq_window_start") < F.lit(floor).cast("date"))
            & (F.col("a3_pre_dlq_payment_level") == "no_record")
            & F.col("pre_dlq_reason").isNull()
        )
        lines += [
            f"no record with the window starting before the floor {floor}: {cut.count()}"
        ]
    lines += ["Dimension B level:"] + _counts(pay, ["a3_dlq_payment_level"], n)
    _block("A3 EPISODE", lines)


def create_a3_check_pipeline(product: str, dues, payments) -> Pipeline:
    """The latest month through the A3 engine in the ``a3_check`` namespace (nothing real
    is overwritten): payments judge, DCORE judge and uncapped contacts, then the blocks.
    """
    p = f"crx_{product}_a3"
    obs = f"crx_{product}_obs_base"
    base = create_a3_pipeline(
        product, f"{p}_check_payments", dues, payments, kept_by="payments"
    )
    inputs = {i for i in base.inputs() if not i.startswith("params:")} - {obs}
    params = {i for i in base.all_inputs() if i.startswith("params:")}
    scoped = pipeline(
        base,
        namespace=NS,
        inputs={**{i: i for i in inputs}, obs: f"{NS}.obs_latest"},
        outputs={f"{p}_check_payments": f"{p}_check_payments"},
        parameters=params,
    )

    def ns(name: str) -> str:
        return f"{NS}.{name}"

    signals = {
        "episode": ns(f"{p}_episode"),
        "instalments": ns(f"{p}_instalments"),
        "payments": ns(f"{p}_payments"),
        "dues": ns(f"{p}_dues"),
    }
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
            func=partial(
                build_commitment_signals, kept_by="dcore", grace=GRACE[product]
            ),
            inputs=signals,
            outputs=ns("commitments_dcore"),
            name=f"{p}_check_commitments_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_a3_credibility, kept_by="dcore"),
            inputs={
                "episode": signals["episode"],
                "commitments": ns("commitments_dcore"),
                "dlq_payments": ns(
                    f"{p}_dlq_payment_signals_single_payment_cycle_count"
                ),
                "pre_dlq": ns(
                    f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
                ),
                "contacts": ns(f"{p}_strong_negative_signals"),
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=f"{p}_check_dcore",
            name=f"{p}_check_state_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_contact_signals, max_months=None),
            inputs={
                "episode": signals["episode"],
                "followup": "dcore_prm_followup_outcomes",
                "agreements": "prm_dcore_account_agreements",
                "instalments": signals["instalments"],
                "payments": signals["payments"],
                "dues": signals["dues"],
                "model_id": "params:model_id",
            },
            outputs=ns("contacts_uncapped"),
            name=f"{p}_check_contacts_uncapped",
            tags=TAGS,
        ),
        node(
            func=partial(compare_a3, floor=None) if product == "rl" else compare_a3,
            inputs={
                "old": f"{p}_payment_credibility",
                "pay": f"{p}_check_payments",
                "dcore": f"{p}_check_dcore",
                "uncapped": ns("contacts_uncapped"),
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
                **(
                    {}
                    if product == "rl"
                    else {"floor": "params:cc_a3_history_floor_date"}
                ),
            },
            outputs=None,
            name=f"{p}_check_compare",
            tags=TAGS,
        ),
    ]
    return scoped + Pipeline(extra)
